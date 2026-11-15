# This repository is linked directly into AtomVM's ESP-IDF components folder.
idf_component_register(
  SRCS
    "components/papapa_audio/audio_nif.c"
    "components/papapa_audio/audio_catalog.generated.c"
  INCLUDE_DIRS
    "components/papapa_audio"
  PRIV_REQUIRES
    libatomvm
    avm_sys
    esp_driver_ledc
    esp_driver_gptimer
    esp_driver_gpio
    esp_timer
  WHOLE_ARCHIVE
)
