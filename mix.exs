defmodule HelloAtomvmPapapa.MixProject do
  use Mix.Project

  def project do
    [
      app: :hello_atomvm_papapa,
      version: "0.1.0",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      atomvm: [start: HelloAtomvmPapapa],
      deps: deps()
    ]
  end

  def application, do: [extra_applications: []]

  defp deps do
    [
      {:exatomvm, git: "https://github.com/atomvm/exatomvm", ref: "14c293b", runtime: false},
      {:atomvm, "== 0.7.0-beta.0", runtime: false}
    ]
  end
end
