defmodule HelloAtomvmPapapa.Catalog do
  @moduledoc "Generated track IDs matching the native C audio catalog."
  @tracks [
    {"smoke", 0, 2000},
    {"demo_papageno", 1, 10200},
    {"demo_papagena", 2, 10200},
    {"demo_duet", 3, 10200},
    {"tone_440", 4, 6000}
  ]

  def names, do: Enum.map(@tracks, fn {name, _id, _duration} -> name end)

  def id(name) do
    case Enum.find(@tracks, fn {track, _id, _duration} -> track == name end) do
      {_name, id, _duration} -> id
      nil -> nil
    end
  end

  def duration_ms(name) do
    case Enum.find(@tracks, fn {track, _id, _duration} -> track == name end) do
      {_name, _id, duration} -> duration
      nil -> nil
    end
  end
end
