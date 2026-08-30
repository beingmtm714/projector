import sys, pathlib
kit = pathlib.Path('_kit.txt').read_text()
TPL = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
{kit}
{body}
</x-dc>
<script data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""
name, w, h = sys.argv[1], sys.argv[2], sys.argv[3]
body = pathlib.Path('_body_'+name+'.html').read_text()
out = TPL.format(kit=kit, body=body, w=w, h=h)
pathlib.Path(name+'.dc.html').write_text(out)
print('wrote', name+'.dc.html')

# One copy. build-wireframes.py reads this folder directly, so there is nothing
# to keep in step. Run ../tools/build-wireframes.py after this.
