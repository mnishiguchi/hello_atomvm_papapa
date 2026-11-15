defmodule HelloAtomvmPapapa.CatalogTest do
  use ExUnit.Case, async: true

  alias HelloAtomvmPapapa.{Catalog, Player}

  test "catalog has an individually selectable singer and a duet" do
    assert is_integer(Catalog.id("demo_papageno"))
    assert is_integer(Catalog.id("demo_papagena"))
    assert is_integer(Catalog.id("demo_duet"))
    assert Catalog.id("not_there") == nil
  end

  test "unknown clips are rejected before calling native code" do
    assert Player.play("unknown", 7) == {:error, {:unknown_track, "unknown"}}
  end

  test "host without a custom native runtime reports missing NIF" do
    assert Player.play("demo_papageno", 7) == {:error, :native_component_missing}
  end
end
