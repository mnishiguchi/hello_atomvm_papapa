defmodule HelloAtomvmPapapa.Player do
  @moduledoc "Small Elixir control layer; timing-sensitive playback stays in native C."

  alias HelloAtomvmPapapa.{Catalog, Native}

  @spec play(binary(), non_neg_integer()) :: :ok | {:error, term()}
  def play(track, gpio) when is_binary(track) and is_integer(gpio) do
    case Catalog.id(track) do
      nil ->
        {:error, {:unknown_track, track}}

      id ->
        case Native.init(gpio) do
          0 -> start_track(id)
          code when is_integer(code) -> {:error, {:native_init_failed, code}}
          other -> {:error, {:unexpected_native_result, other}}
        end
    end
  catch
    :error, :nif_not_loaded -> {:error, :native_component_missing}
  end

  def play(track, _gpio), do: {:error, {:invalid_track, track}}

  @spec start_track(non_neg_integer() | nil) :: :ok | {:error, term()}
  def start_track(nil), do: {:error, :unknown_track}

  def start_track(id) when is_integer(id) and id >= 0 do
    case Native.play(id) do
      0 -> :ok
      code when is_integer(code) -> {:error, {:native_play_failed, code}}
      other -> {:error, {:unexpected_native_result, other}}
    end
  catch
    :error, :nif_not_loaded -> {:error, :native_component_missing}
  end
end
