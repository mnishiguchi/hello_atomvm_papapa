defmodule HelloAtomvmPapapa.Native do
  @moduledoc """
  Stubs replaced by AtomVM's registered native NIF collection.

  Requires a custom ESP32-C5 AtomVM firmware containing this repository's
  CMake component. The default AtomVM firmware does not provide these NIFs.
  """

  def init(_gpio), do: :erlang.nif_error(:nif_not_loaded)
  def play(_track_id), do: :erlang.nif_error(:nif_not_loaded)
  def stop, do: :erlang.nif_error(:nif_not_loaded)
  def busy, do: :erlang.nif_error(:nif_not_loaded)
  def duration_ms(_track_id), do: :erlang.nif_error(:nif_not_loaded)
  def skipped_samples, do: :erlang.nif_error(:nif_not_loaded)
end
