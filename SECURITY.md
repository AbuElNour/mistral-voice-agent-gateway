# Security

Audio frames are processed in memory and are not persisted. Duplicate frames are ignored, retries are bounded, and fixtures contain only synthetic phrases. Production channel authentication and webhook validation belong in provider adapters, never in committed configuration.

