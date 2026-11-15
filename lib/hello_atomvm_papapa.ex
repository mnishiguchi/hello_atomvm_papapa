defmodule HelloAtomvmPapapa do
  @moduledoc "AtomVM entrypoint: play one short singer clip through GPIO7 PWM."

  alias HelloAtomvmPapapa.{Catalog, Native, Player}

  # Build-time settings, because the ESP32 firmware has no shell environment.
  @track System.get_env("PAPAPA_TRACK") || "demo_papageno"
  @repeat_enabled System.get_env("PAPAPA_REPEAT") == "true"
  @gpio 7

  def start do
    :erlang.display({:papapa, :boot, @track, :gpio7})

    case Player.play(@track, @gpio) do
      :ok ->
        wait_until_finished(@track, @repeat_enabled)

      {:error, reason} ->
        :erlang.display({:papapa, :error, reason})
        idle()
    end
  end

  defp wait_until_finished(track, repeat_enabled) do
    Process.sleep(250)

    case Native.busy() do
      1 ->
        wait_until_finished(track, repeat_enabled)

      0 ->
        :erlang.display({:papapa, :finished, track, :skipped_samples, Native.skipped_samples()})

        if repeat_enabled do
          Process.sleep(800)

          case Player.start_track(Catalog.id(track)) do
            :ok ->
              wait_until_finished(track, true)

            error ->
              :erlang.display({:papapa, :replay_error, error})
              idle()
          end
        else
          idle()
        end

      other ->
        :erlang.display({:papapa, :unexpected_busy, other})
        idle()
    end
  end

  defp idle do
    Process.sleep(60_000)
    idle()
  end
end
