# Supply Drop BBS

A Home Assistant App packaging of Mesh America's Supply Drop BBS for MeshCore and Meshtastic radio networks.

The App downloads and verifies the official upstream release binary during the image build. Runtime state is stored in `/data`, while the generated upstream `config.toml` is exposed through the App configuration folder.
