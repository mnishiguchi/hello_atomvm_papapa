.PHONY: check test format-check preview

check: test format-check

test:
	python3 scripts/test_assets.py
	python3 scripts/test_commands.py
	elixir scripts/test_host.exs

format-check:
	mix format --check-formatted

preview:
	python3 scripts/build_assets.py --preview-dir preview
