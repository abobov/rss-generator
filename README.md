# RSS generator for sites

## Quick start

Create a virtual environment

```
virtualenv venv
```

Activate the virtual environment

```
source venv/bin/activate
```

Install libraries

```
pip install -r requirements.txt
```

And now you can run RSS generation

```
python3 main.py --output feed.xml URL
```

## Supported sites

List of supported sites in [the plugins directory](plugins).

If your site is not supported, then you need to implement a plugin like others
or ask for help as [a new issue](https://github.com/abobov/rss-generator/issues/new).
