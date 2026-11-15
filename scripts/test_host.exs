# Compile the entrypoint as well as the control modules without fetching Mix deps.
Code.require_file("../lib/hello_atomvm_papapa/catalog.ex", __DIR__)
Code.require_file("../lib/hello_atomvm_papapa/native.ex", __DIR__)
Code.require_file("../lib/hello_atomvm_papapa/player.ex", __DIR__)
Code.require_file("../lib/hello_atomvm_papapa.ex", __DIR__)
Code.require_file("../test/test_helper.exs", __DIR__)
Code.require_file("../test/catalog_test.exs", __DIR__)
