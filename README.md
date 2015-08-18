# Color Extractor Bench

## Generate all fixtures

`make generate`


## Ruby

```
cd ruby
bundle exec ruby color_extractor.rb -i ../fixtures/103406.jpg -o output/103406_default_palette.jpg
bundle exec ruby color_extractor.rb -p ../colors.yaml -i ../fixtures/103406.jpg -o output/103406_custom_palette.jpg

```

## Python

```
python color_extractor_rgb.py -i ../fixtures/103406.jpg -o output/103406.jpg -c 7 -p ../colors.yaml
```
