generate: clean
	for file in fixtures/*; \
	do \
		echo $$file; \
		BUNDLE_GEMFILE=./ruby/Gemfile bundle exec ruby ruby/color_extractor.rb -i $$file -o output/$$(basename $$file).ruby.default_palette.png; \
		BUNDLE_GEMFILE=./ruby/Gemfile bundle exec ruby ruby/color_extractor.rb -i $$file -p colors.yaml -o output/$$(basename $$file).ruby.custom_palette.png; \
		python python/color_extractor_rgb.py -i $$file -o output/$$(basename $$file).python.png -c 7 -p colors.yaml; \
	done

clean:
	rm -rf output/*
