import geobuf
import json
import subprocess
import glob
import os.path
import shutil

exclude = {'precision.json'}
files = glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/*.json"))
forward_fixtures = [filename for filename in files if os.path.basename(filename) not in exclude]

# python encode -> javascript decode incompatibilities:
#   - features containing both geojson properties and custom properties
#   - empty geometries
reverse_fixtures = [
    filename for filename in forward_fixtures
    if os.path.basename(filename) != 'props.json'
    and not os.path.basename(filename).startswith('empty-')
]


def test_forward(filename):
    """javascript encode, python decode"""
    with open(filename) as f:
        expected_geojson = json.loads(f.read())
    print(filename)
    result = subprocess.run(['json2geobuf', filename], stdout=subprocess.PIPE)
    pbf = result.stdout
    decoded = geobuf.decode(pbf)
    geojson = json.loads(json.dumps(decoded))
    try:
        assert geojson == expected_geojson
    except AssertionError:
        print('{} \n != \n {}'.format(geojson, expected_geojson))
        raise


def test_reverse(filename):
    """python encode, javascript decode"""
    print(filename)
    with open(filename) as f:
        geojson_str = f.read()
    expected_geojson = json.loads(geojson_str)
    pbf = geobuf.encode(expected_geojson)
    result = subprocess.run(['geobuf2json'], stdout=subprocess.PIPE, input=pbf)
    json_str = result.stdout.decode('utf-8')
    geojson = json.loads(json_str)
    try:
        assert geojson == expected_geojson
    except AssertionError:
        print('{} \n != \n {}'.format(geojson, expected_geojson))
        raise


if __name__ == '__main__':
    """Run fixtures through the between the javascript and python implementations"""
    if not shutil.which('json2geobuf'):
        raise RuntimeError('You must run npm install -g geobuf@<version> prior to running the round trip tests.')

    for filename in forward_fixtures:
        test_forward(filename)

    for filename in reverse_fixtures:
        test_reverse(filename)
