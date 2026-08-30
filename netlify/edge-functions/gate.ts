// Access gate for /docs/private/* — the investor deck and the pre-seed memo.
//
// Anyone without a valid token gets a hard 401. There is no soft redirect and
// no client-side check: the page body is never sent to an unauthorised caller.
//
// Two ways in:
//   1. ?k=<token> on the URL. Valid tokens get a cookie and a redirect to the
//      clean URL, so the token stops appearing in the address bar, in browser
//      history, and in any Referer header the page later emits.
//   2. The cookie set by step 1, for subsequent requests.
//
// Tokens live in the PROJECTOR_TOKENS environment variable, never in this file.
// Shape: { "<token>": { "label": "Who this was issued to", "paths": ["/docs/private/investor-deck.html"] } }
// A paths entry of ["*"] grants access to everything under /docs/private/.

import type { Config, Context } from "https://edge.netlify.com";

const COOKIE = "projector_access";
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

type Grant = { label: string; paths: string[] };

function loadTokens(): Record<string, Grant> {
  const raw = Netlify.env.get("PROJECTOR_TOKENS");
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, Grant>;
  } catch {
    // A malformed variable must fail closed, never open.
    return {};
  }
}

// Length-independent compare. Overkill for 256-bit random tokens over a
// network, but it costs nothing and removes the question.
function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function resolve(token: string | null, tokens: Record<string, Grant>): Grant | null {
  if (!token) return null;
  for (const [known, grant] of Object.entries(tokens)) {
    if (safeEqual(token, known)) return grant;
  }
  return null;
}

function permits(grant: Grant, pathname: string): boolean {
  return grant.paths.some((p) => p === "*" || pathname.startsWith(p));
}

function readCookie(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [k, ...rest] = part.trim().split("=");
    if (k === name) return rest.join("=");
  }
  return null;
}

function denied(): Response {
  return new Response(DENIED_HTML, {
    status: 401,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow, noarchive, nosnippet",
    },
  });
}

export default async (request: Request, context: Context) => {
  const url = new URL(request.url);
  const tokens = loadTokens();

  // No tokens configured means the gate is misconfigured. Fail closed.
  if (Object.keys(tokens).length === 0) return denied();

  // 1. Token on the URL — validate, set cookie, redirect to the clean path.
  const queryToken = url.searchParams.get("k");
  if (queryToken) {
    const grant = resolve(queryToken, tokens);
    if (grant && permits(grant, url.pathname)) {
      // Loop guard: if the cookie already carries this token, serve the page
      // instead of redirecting again. Without this, any failure to strip ?k
      // from the Location header becomes an infinite redirect.
      const existing = readCookie(request.headers.get("cookie"), COOKIE);
      if (existing && safeEqual(decodeURIComponent(existing), queryToken)) {
        return;
      }

      // Rebuild the query string explicitly rather than mutating searchParams,
      // so the token does not survive into the address bar or browser history.
      const params = new URLSearchParams(url.search);
      params.delete("k");
      const qs = params.toString();
      // Absolute, not relative: Netlify's proxy re-attaches the original query
      // string to relative Location headers, which put ?k= straight back on.
      const target = `${url.origin}${url.pathname}${qs ? `?${qs}` : ""}`;

      return new Response(null, {
        status: 302,
        headers: {
          location: target,
          "set-cookie":
            `${COOKIE}=${encodeURIComponent(queryToken)}; Path=/p/; Max-Age=${MAX_AGE};` +
            ` HttpOnly; Secure; SameSite=Lax`,
          "cache-control": "no-store",
          "x-gate": "v4",
        },
      });
    }
    return denied();
  }

  // 2. Returning visitor — cookie must still be valid for THIS path, so a
  //    token issued for one proposal cannot be reused on another.
  const cookieToken = readCookie(request.headers.get("cookie"), COOKIE);
  const grant = resolve(cookieToken ? decodeURIComponent(cookieToken) : null, tokens);
  if (grant && permits(grant, url.pathname)) {
    return; // authorised — continue to the static file
  }

  return denied();
};

export const config: Config = {
  path: "/docs/private/*",
  // The gate itself must never be cached at the edge, or one authorised
  // response could be replayed to an anonymous caller.
  cache: "manual",
};

const DENIED_HTML = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Bastille Advisory</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--ink:oklch(12% 0.008 260);--ink-3:oklch(44% 0.008 260);--paper:oklch(98% 0.008 87);--pink:oklch(54% 0.28 8);--rule:oklch(85% 0.010 87)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:'Barlow',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;border-top:3px solid var(--pink)}
.card{max-width:420px;text-align:left}
.brand{font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:.18em;line-height:1}
.sub{font-size:.55rem;font-weight:600;letter-spacing:.28em;text-transform:uppercase;color:var(--pink);margin-top:3px}
h1{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:.04em;margin:32px 0 12px}
p{font-size:.95rem;color:var(--ink-3);line-height:1.7;margin-bottom:10px}
a{color:var(--pink)}
hr{border:0;border-top:1px solid var(--rule);margin:28px 0}
</style></head><body>
<div class="card">
  <div class="brand">BASTILLE</div><div class="sub">Advisory</div>
  <h1>This document is private</h1>
  <p>It opens only from the link it was sent with. If you have that link, open it again in full, including everything after the question mark.</p>
  <hr>
  <p>Need a fresh link? <a href="mailto:michael@bastilleadvisory.xyz">michael@bastilleadvisory.xyz</a></p>
</div></body></html>`;
