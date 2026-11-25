# AirGradient hardware

Open hardware design files for the AirGradient monitors whose firmware lives in this repository. Retrieved 2026-11-25. Nothing in this tree was redrawn: each file is an extract of a file AirGradient published, aside from the editor junk called out below.

## License and attribution

AirGradient publishes these designs under the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0). The builds overview says: "All builds are licensed under CC BY-SA 4.0. Please ensure proper attribution."

- Attribute **AirGradient** (https://www.airgradient.com/).
- If you modify the schematic, PCB, or enclosure and share that modification, license the modification under CC BY-SA 4.0 as well.
- The full license text is in [`LICENSE`](LICENSE), the same CC BY-SA 4.0 legal code used for this firmware repository. AirGradient's download archives do not include a separate license file.

Some component symbols, footprints, and 3D models bundled inside the KiCad projects carry their own upstream terms. In particular, `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/License.txt` is the SnapEDA agreement that shipped with the ESP32-C3 model. Those files are kept as they were published.

## What this covers

The current AirGradient Open Air outdoor monitor is model **O-1PST** (PCB silkscreen **V 1.3**). Models **O-1PP**, **O-1PPT**, and **O-1PS** use this same main board. The firmware picks the variant from which sensors are fitted:

| Model | PM channels | SenseAir S8 CO2 module | SGP41 module |
| --- | --- | --- | --- |
| O-1PST | 1 (PM1) | yes, on the PM2 connector | yes, on I2C1 |
| O-1PS | 1 | yes | no |
| O-1PPT | 2 | no | yes |
| O-1PP | 2 | no | no |

The Plantower PMS5003T plugs into the PicoBlade sockets on the main board and has no carrier PCB of its own.

## Layout

Schematic and PCB stay in one directory per board. KiCad resolves symbols, footprints, and 3D models through `${KIPRJMOD}` paths in `fp-lib-table` and `sym-lib-table`, so splitting `.kicad_sch` from `.kicad_pcb` would stop the project from opening.

| Path | Contents |
| --- | --- |
| `open-air/main-board/` | Open Air main board, KiCad project `ag_outdoor` (schematic, layout, libraries, Gerbers, BOM, pick-and-place) |
| `open-air/sgp41-module/` | SGP41 TVOC/NOx module, KiCad sources plus the released Gerbers and BOM |
| `open-air/co2-module/` | SenseAir S8 / Sunlight CO2 carrier, KiCad project `CO2-sensor-pcb` plus Gerbers and BOM |
| `open-air/enclosure/` | 3D-printable enclosure STLs |

Open a project by loading its `.kicad_pro` (or the `.kicad_pcb` / `.kicad_sch` next to it) in KiCad. The main board and CO2 carrier are KiCad 7 files (`kicad_pcb` version 20221018, schematic version 20230121). The SGP41 module is an older KiCad 6 project (`kicad_pcb` version 20211014) whose schematic and board were saved as two project names in the same folder (`sgp41-tvoc-sensor-module` and `tvoc-sensor-module`). That split is how AirGradient published the archive.

## Sources

### Main board — PCB V 1.3

- Source: https://www.airgradient.com/documents/gerber/openair-v13-kicad.zip
- Linked from the O-1PST row of https://www.airgradient.com/documentation/kb/kb-diy-the-airgradient-builds-overview as "KiCad files"
- Hardware revision: V 1.3 (silkscreen text `V 1.3`; archive folder `ag_outdoor.V1.3`). Board file dated 2023-11-22 inside the archive, which AirGradient packaged on 2024-09-12.
- Retrieved: 2026-11-25
- License: CC BY-SA 4.0, AirGradient
- Editable source: KiCad schematic (`.kicad_sch`), PCB (`.kicad_pcb`), project, and the symbol/footprint libraries the project references. No separate schematic PDF is in the archive.

### SGP41 module — V3

- KiCad source: https://www.airgradient.com/documents/gerber/SGP41-sensor-module_V3.zip
- Linked from the same O-1PST row as "SGP41 Module" (the indoor ONE row links this same zip).
- Hardware revision: V3. Silkscreen reads `SGP41 3.0`. PCB file dated 2023-05-22.
- Retrieved: 2026-11-25
- License: CC BY-SA 4.0, AirGradient
- The airgradient.com zip contains the KiCad project and libraries. It does not contain Gerbers or a BOM.
- Gerbers and BOM below are the released production set AirGradient kept in Bitbucket repository `airgradient/sgp41-tvoc-sensor-module` (commit `5fa8f8e`). That Bitbucket project is no longer public. The files are the copy imported, without design changes, by https://github.com/Open-Air-Foundation/pcb-module-sgp41 (commit `eb3bd83093`, file `sgp41-tvoc-sensor-module/production/tvoc-sensor-module-v3.zip` and `sgp41-tvoc-sensor-module/BOM/sgp41-bom.xls`). Gerber timestamps are 2023-05-22 11:31, the same timestamp as `tvoc-sensor-module.kicad_pcb` in the airgradient.com zip. Retrieved 2026-11-25. License stated on that repository: CC BY-SA 4.0, AirGradient.

### CO2 module — V1

- Source: https://www.airgradient.com/documents/gerber/openair-CO2-pcb-v1.zip
- Linked from the O-1PST row as "CO2 Module"
- Hardware revision: V1 (archive folder `CO2-sensor-pcb_V1`). Board file dated 2024-01-27. Silkscreen marks both an S8 and a SUN (SenseAir Sunlight) footprint.
- Retrieved: 2026-11-25
- License: CC BY-SA 4.0, AirGradient
- Editable source: KiCad schematic and PCB. Gerbers, BOM (`BOM.xls`), centroid (`CO2-sensor-pcb-all-pos.csv`), and a Gerber zip are in `gerber_output/`. The archive's `Library.pretty/` directory was empty and is not included.

### Enclosure

- Source: https://www.airgradient.com/documents/3d/diy_outdoor_3d.zip
- Linked from the O-1PST row as "STL Files". The same zip is the enclosure download on the older outdoor DIY build page (https://www.airgradient.com/documentation/kb/kb-old-instructions-the-airgradient-diy-outdoor-air-quality-monitor).
- Revision: no revision string in the files. Archive members are dated 2022-12-09. Three binary STL parts: top, and a two-piece bottom.
- Retrieved: 2026-11-25
- License: CC BY-SA 4.0, AirGradient
- Format: STL only. These are the 3D-printable enclosure AirGradient publishes for this outdoor board. They are not a STEP or CAD source of the injection-molded ASA case sold with the pre-assembled kit.

## Not publicly available

Searched on 2026-11-25: the AirGradient builds overview, the O-1PST PCB 1.3 build instructions, the PCB 1.1 technical documentation, the outdoor product page (https://www.airgradient.com/outdoor/), and the `airgradienthq` GitHub account. The public Bitbucket workspace `airgradient` currently lists no repositories.

- **Schematic PDF.** Not published for V 1.3, the SGP41 module, or the CO2 module. The editable file is the KiCad schematic. The archived PCB 1.1 technical page shows a schematic as a web image, not as a PDF download, and that image is for the older 1.1 board rather than V 1.3.
- **Enclosure STEP, 3MF, or CAD source.** Not published. The O-1PST build instructions say "enclosure step files" are available, but the only enclosure link on the Open Air row and on the outdoor DIY page is `diy_outdoor_3d.zip`, which contains the three STLs above. Direct guesses for a STEP archive under `www.airgradient.com/documents/3d/` returned 404. No enclosure repository is published under `airgradienthq` or Open-Air-Foundation.
- **EasyEDA source.** These boards were published as KiCad.
- **SGP41 Gerbers and BOM on airgradient.com.** Not in `SGP41-sensor-module_V3.zip`. The copies under `open-air/sgp41-module/production/` are the Bitbucket production set described above.
- **Injection-molded production enclosure.** No public mechanical file beyond the DIY STLs.
- **Older boards, not vendored here.** PCB 1.1 KiCad is still linked from the archived technical page as https://www.airgradient.com/documents/gerber/openair-v11-kicad.zip. The ESP8266 outdoor board (PCB 0.4) is a different design: https://www.airgradient.com/documents/gerber/gerber_diy_outdoor.zip. The builds overview lists only the V 1.3 KiCad archive for the current Open Air.
- **Optional boards that are not the shared Open Air PCB.** The cellular model (O-1PST-CE) uses a separate CE card. A KiCad import of that card is at https://github.com/Open-Air-Foundation/pcb-module-ce-card. It is not linked from the Open Air row. The SHT4x module (https://www.airgradient.com/documents/gerber/SHT4X-sensor-module_V1.zip) is listed for the indoor ONE and Open Air Max, not for O-1PST. Open Air temperature and humidity come from the PMS5003T.

## Omitted from the archives

These members of the official zips were not design files:

- `__MACOSX/` and AppleDouble `._*` resource-fork files
- `fp-info-cache` (KiCad footprint cache)
- `_autosave-ag_outdoor.kicad_sch` (an editor autosave; it is not identical to `ag_outdoor.kicad_sch`)
- `~ag_outdoor.kicad_sch.lck` and `#auto_saved_files#`
- `Library.bak` on the main board (an empty symbol-library backup)
- `CO2-sensor-pcb_V1/Library.pretty/` (empty directory)

`open-air/sgp41-module/libs/SGP4X/SGP4x.bak` is a 73-byte backup that was inside the published SGP41 zip, so it is kept.

## File inventory

Size is in bytes. SHA-256 is of the file as committed. Retrieved 2026-11-25. License for every design file: CC BY-SA 4.0, AirGradient, except the third-party component license noted above.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `open-air/co2-module/CO2-sensor-pcb.kicad_pcb` | 122431 | `dbf6768c0feed4f4f155a920749afc0a23dd7321d4a73149ae1ffc3d94d1a4f4` |
| `open-air/co2-module/CO2-sensor-pcb.kicad_prl` | 1282 | `81177da3e68ff7bf83fc35a68b714d1e39bef266d5a48a27ac3fda71b05d8a9f` |
| `open-air/co2-module/CO2-sensor-pcb.kicad_pro` | 12832 | `5ffde56d521b347ac782448195e0acc036e639a448737937b0663603a3400f26` |
| `open-air/co2-module/CO2-sensor-pcb.kicad_sch` | 70416 | `eeddb43834b36029a7fafe2fa015944b58d29615b255db386c43468620371c98` |
| `open-air/co2-module/gerber_output/BOM.xls` | 36864 | `8ec88ac38e1f8d77ea5c5b8e5cbb038440c27f2d8429ab7a608d51f9489d7e55` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-B_Cu.gbl` | 8603 | `38b4c59bf5cb0e6e72025100af5876b86ec96aec15795b5fbad18088dad28717` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-B_Mask.gbs` | 2531 | `cba12e95fa07ecefb86d5ae0f168d988e262ef986706342bc9d30f3127f8a340` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-B_Paste.gbp` | 508 | `71cc43159d1f6b895d2135bd1525e280c9d6d1b453c57a441597204c04b951a1` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-B_Silkscreen.gbo` | 30923 | `d8688d7cbec8725d97efba426bcaa8483bd95779c7ed00c6a6a418668d4b2cd3` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-Edge_Cuts.gm1` | 2033 | `318ee1be5add0d5b935886c7ad2aefc58682eec2cd1e86a8ea81124b8184d9be` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-F_Cu.gtl` | 11482 | `efea468431f8998e4299196c10167c6924a681ffb2471f0c0eaef848b7627054` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-F_Mask.gts` | 3535 | `762936f765c5cff0020b56fec4517a4fb08c8017ef9a85703c8c829c704f4b73` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-F_Paste.gtp` | 2124 | `f7ccf50749bc710a43d5d785dc08884fc8940fa686497f4e016a8c95b85b366a` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-F_Silkscreen.gto` | 31429 | `5ddf471d2086f2efba98c7b88f539fe829c1c4933363373ff18faa5fe0bc7d2b` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-NPTH-drl_map.gbr` | 23485 | `09a2d600ad5515b9159b9ceff73e232c8da4d330601e18b36b03a30bf0425d7e` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-NPTH.drl` | 382 | `7f1a02428aa593e228ed688c9d692d718b892e0ee79313dc7fb52e7f63811343` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-PTH-drl_map.gbr` | 32852 | `928152d9dd134c12a2bac022252b893b24c04003a6048c3d9fce4fc4f91e4fd8` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-PTH.drl` | 867 | `ff731d8239e30d43474edb41e6234f2a48207aafc927de61fff96553f795d772` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb-all-pos.csv` | 315 | `4473482aee612c67f99c9c318274eb482584bb2124ce73450fd4cd5097d7678b` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb.csv` | 645 | `54e72c078ceca1216afc0faa05da81eca3deb6c51ea5ba9ef2560cf282f8e2e3` |
| `open-air/co2-module/gerber_output/CO2-sensor-pcb.zip` | 30698 | `7a74264442b13a7e3873e38ee8064f470d5b91a99cb3de6bb487d0ea3db352e1` |
| `open-air/enclosure/AirGradient Outdoor DIY Bottom Part A.stl` | 2606584 | `125d6e4342822cea196a305598bffcf22c5484c719ab489d5d03ae02be6fa536` |
| `open-air/enclosure/AirGradient Outdoor DIY Bottom Part B.stl` | 601184 | `617d2ba83dd75e01411b122f1f918ce0eaad6637b047545ffc6ed11592a78a9c` |
| `open-air/enclosure/AirGradient Outdoor DIY Top Part C.stl` | 615884 | `9f020a86c754f689c81a80471c3e06fe7169285b40226a3cd03a2e25ad12d36f` |
| `open-air/main-board/BOM/BOM.xls` | 38912 | `7bca422c24bfc699b13a3d55d6151962b7472152ae332149b3f2a111c6bd4889` |
| `open-air/main-board/BOM/ag_outdoor.csv` | 1104 | `5b586f36e0ec31646904cc4e27d0d232ea26ce1edc7e5e80bfd4e73c71065bd3` |
| `open-air/main-board/Gerber_Output/ag_outdoor-B_Cu.gbl` | 77488 | `7e758b95540c335d7e3475b2412822f7c8620b3ca19a475792f54222f37eb29c` |
| `open-air/main-board/Gerber_Output/ag_outdoor-B_Mask.gbs` | 1217 | `dfdc0fd8ec09dd066c93260ff9937894fe14398759378dfa4c1a231d804c207d` |
| `open-air/main-board/Gerber_Output/ag_outdoor-B_Paste.gbp` | 504 | `85d73382b3df26fed7e5b77245a3df6825104b8a9a2157e0bc4fe573b678a9fe` |
| `open-air/main-board/Gerber_Output/ag_outdoor-B_Silkscreen.gbo` | 115747 | `cce93fbec52c9a835623f3572b2c073bad835acddd085240bbfa2a6c86262068` |
| `open-air/main-board/Gerber_Output/ag_outdoor-Edge_Cuts.gm1` | 15424 | `ab360f76bf145383cf156c4dd44b30ecc1f857e573139f2e19392bcd6e4382f7` |
| `open-air/main-board/Gerber_Output/ag_outdoor-F_Cu.gtl` | 155294 | `0898dac2acd20d3764e7eb4672a2f23e1d2a007b4979a527b61e089fe519fa4b` |
| `open-air/main-board/Gerber_Output/ag_outdoor-F_Mask.gts` | 9314 | `2201442c928bc1f1fc21d3ae9386f717ded1c17be1621e3911fdaa71d6ab98ee` |
| `open-air/main-board/Gerber_Output/ag_outdoor-F_Paste.gtp` | 8205 | `20618b98d708fd07ec1aa937a8d2fa6861cb6c722f40794b893a2e1240ed42d4` |
| `open-air/main-board/Gerber_Output/ag_outdoor-F_Silkscreen.gto` | 83661 | `6631247f00b6fbe74e0e9efb23453c1ca4469e2dbf50ccb4aebebee0803dd6ed` |
| `open-air/main-board/Gerber_Output/ag_outdoor-NPTH-drl_map.gbr` | 37721 | `329f904a6be7b4699186146f8f72cbfe875fc6024efd7f2e06b3add1863493fc` |
| `open-air/main-board/Gerber_Output/ag_outdoor-NPTH.drl` | 386 | `65127704fd6944fa357e48adaf24cb77f4dde0e9b432416159c10d1b25cb3454` |
| `open-air/main-board/Gerber_Output/ag_outdoor-PTH-drl_map.gbr` | 146657 | `aaf3e3ed35c85fb0b0d3ac9346681e346682e7179085864d7ed93d3165256e8b` |
| `open-air/main-board/Gerber_Output/ag_outdoor-PTH.drl` | 2615 | `d3467e49c9e6745469db19c79bd842e8d013f0d243e50e5d7e8f9373b4ccecf4` |
| `open-air/main-board/Gerber_Output/ag_outdoor-all-pos.csv` | 2783 | `4841c6e1445d2fe94728814a8629a927e5ef7da5d9e8847afc16f763d6d1ffcc` |
| `open-air/main-board/Library.kicad_sym` | 12979 | `033986f4f43a81880bcfea63dc2265f425bb59a8eff521233130c2ebab60e6d2` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/ESP32-C3-MINI-1-N4.kicad_sym` | 14944 | `a8c59ef0a02a402df50393782d73eb5c64ca5bb311fbede282863dea6839d1dd` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/ESP32-C3-MINI-1-N4.step` | 2023564 | `d9e51f34f235332f4d80665c86e9cd9f6434f26a00901bc4957ec6cd9061bf0e` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/License.txt` | 2978 | `4450ceed47935c294b35015e2864c66d91fb46850d1cf2a6f5d4417c1a2ca1f9` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/XCVR_ESP32-C3-MINI-1-N4.kicad_mod` | 8222 | `4ac553856de7b58c0b50e39dc71c9620a5109f89146b52d6642b01cdef2128eb` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4/how-to-import.htm` | 445 | `24e9a101a0ca11ff7db51062503d7e4ccdb70678f037eea9b38e7e61a762634f` |
| `open-air/main-board/Libs/ESP32-C3-MINI-1-N4.pretty/XCVR_ESP32-C3-MINI-1-N4.kicad_mod` | 13593 | `bcdbf0b853d36cc9cfe04c031bfbd769b96bdb6b24e4c7eb53cd8bf0dd13639e` |
| `open-air/main-board/Libs/IN-S126TASRGB--3DModel-STEP-56544.STEP` | 487068 | `2dfc68fbee7d161c0bbbde365823c7c8415091d76a0b0869e773448f4ef6c3a9` |
| `open-air/main-board/Libs/Library.pretty/LED_D3.0mm.kicad_mod` | 1672 | `685a3165324e9357e865ab8bfe358a91ec7dad77a2234ed7cfc763b97ea5cc0d` |
| `open-air/main-board/Libs/Library.pretty/Logo.kicad_mod` | 51974 | `5f77f16e22945f3e7c2f46fab85c6c883fab7ab2e6945564e0e1615c710e12c1` |
| `open-air/main-board/Libs/Library.pretty/MHS110WDT-C1.kicad_mod` | 860 | `808a776fc559db3708c5ef82032bcb1074709b6827f2cd391b9ddf528e26c59f` |
| `open-air/main-board/Libs/Library.pretty/SOP65P640X120-16N.kicad_mod` | 4806 | `5e897c2f17002cb6050ad161ed9c0fba58429c04a3b8ab12643a188d99b17f36` |
| `open-air/main-board/Libs/Library.pretty/TS-1096-A1B2-D2.kicad_mod` | 4979 | `5852526725d010ff7a5c94291bb0bf66ed9fb4956736f39cf8937706ff9b66c9` |
| `open-air/main-board/Libs/Library.pretty/rohs.kicad_mod` | 27462 | `89fe6c99aae870eafce73ac14de65291d30df66201aa548cd9e9a6d80f4b33eb` |
| `open-air/main-board/Libs/Logo.kicad_mod` | 53584 | `ecc97c06e69fc696836a1f361ebfd4128801b3529af0a062d92d8d71379a0aa0` |
| `open-air/main-board/Libs/SN74LV4052APWR/3D/SN74LV4052APWR.stp` | 181004 | `f6a579760e0c5b7329d2406cbc28bec801e71083164655bc017a43e9d08ca672` |
| `open-air/main-board/Libs/SN74LV4052APWR/3D/SN74LV4052APWR.wrl` | 209925 | `5a2c96504ed70a59a0d4819d92896498a0853a4c284811140983eec97eccb33a` |
| `open-air/main-board/Libs/SN74LV4052APWR/KiCad/SN74LV4052APWR.dcm` | 181 | `e26a692ef7c2f3461f5f2c16aae7269f01c989c0f7960c5c5b1406aecb8b4192` |
| `open-air/main-board/Libs/SN74LV4052APWR/KiCad/SN74LV4052APWR.lib` | 1702 | `af4557eeb2d70406ebcb62daeab94e48fccad0b7f0006148e046a0df50ff1e38` |
| `open-air/main-board/Libs/SN74LV4052APWR/KiCad/SN74LV4052APWR.mod` | 2270 | `0dcf0e991ad81ea792fdb560609baa88f7ec599f7203bf56745c0382ac2a68d1` |
| `open-air/main-board/Libs/SN74LV4052APWR/KiCad/SOP65P640X120-16N.kicad_mod` | 3032 | `442f5dc50a0ecd4f8e9897810b62410db7759a4a84bc5698431201f14acb441d` |
| `open-air/main-board/Libs/SWITCH_xiaobeibei.STEP` | 1159907 | `4bde3bb97e119877f8ee2017a46d59dc53418f053aee3f39782ec61d8bdb38c7` |
| `open-air/main-board/Libs/rohs.kicad_mod` | 27397 | `ccf3545517bb2579889f1db9883bbb76edb7b0df79c9d2e5ecb4129dc8121a86` |
| `open-air/main-board/ag_outdoor.kicad_pcb` | 654065 | `456180ab307b274720a83ec115b316c64238f1f6a9335d8bdaf302bbb689dfd6` |
| `open-air/main-board/ag_outdoor.kicad_prl` | 1299 | `9ffaa9593a2ed6627846827c71ef490d60205aea0c9bce6c960bfd13d0d9be84` |
| `open-air/main-board/ag_outdoor.kicad_pro` | 14725 | `1f96cf0cef124c7ac2b8dd26b3798bb0e63addda856f427a231bc4e4f5072cd6` |
| `open-air/main-board/ag_outdoor.kicad_sch` | 143844 | `5a9061a94486013aa090b35deb126856ee8df396a159dfabbc25c4a0c7286233` |
| `open-air/main-board/fp-lib-table` | 242 | `03e0984d8c8c539c0bef42f437ec5a8cdc06e2411698131e3b03e80a8b57dfca` |
| `open-air/main-board/rohs-mark-icon-isolated-on-white-background-vector.jpg` | 35203 | `083084e8ad328a1f3465d2201ed244606ef8eca9b87e29f7a4648ba81f2aeaab` |
| `open-air/main-board/sym-lib-table` | 118 | `cae480ffd4469b8b814c6a5634530d888f217c75456df938cd7223705f3c8f12` |
| `open-air/sgp41-module/fp-lib-table` | 649 | `0233e015cf7935325811e71f50f7aa575d1e489a2607f6559411ca26257f37d6` |
| `open-air/sgp41-module/icon.png` | 43046 | `a10db6fee7ecf07fdf2fd322af5253e2a0a216a6cc8c22d3df54f71ebd121042` |
| `open-air/sgp41-module/libs/05PSL-JE/05-JE.pretty/05PSL-JE.kicad_mod` | 1815 | `2e33d2956d229360c4b03f9adcd05f0d2d984f6eed952db35b184dc708d4d17d` |
| `open-air/sgp41-module/libs/05PSL-JE/05PSL-JE.STEP` | 265511 | `9d3777f3ea82fc4c22a9b6d2e9973a66322c367fe8c0056e4ea63fd408b6bb16` |
| `open-air/sgp41-module/libs/2N7002DW/2N7002DW.lib` | 1657 | `10f3bfa7dfcd95488f394fd8e79b4eca8b195a391a5adb59943a7c2d0fda2be5` |
| `open-air/sgp41-module/libs/2N7002DW/2N7002DW.step` | 245981 | `83b8d9b77f531379d4a948c6714ad92500957c5f3c7ad505309117fa4f544e2f` |
| `open-air/sgp41-module/libs/2N7002DW/SOT363.kicad_mod` | 1050 | `3c4416942ab894d745c4fe8d82cb3f8393b3d1edbe5c9b093cfc0e4abda2b26a` |
| `open-air/sgp41-module/libs/Horizontal SMT Type Pin header.pretty/PinHeader_1x04_P2.54mm_Horizontal_Short.kicad_mod` | 9877 | `5e6d501e15563a798ff7d8b480ebd0cdf87926c2d9ba8f1b83b7802a3d2b50f3` |
| `open-air/sgp41-module/libs/Horizontal SMT Type Pin header.pretty/h.kicad_mod` | 2120 | `9b3c9d5907cf93304e196921e3a72db698e75d78a01e415118077923f55dc183` |
| `open-air/sgp41-module/libs/Logo.pretty/logo.kicad_mod` | 11899 | `5c42202b1564ac3c4ba0bc61379b70aeed2ba31f9aa295aba1ef81e891783862` |
| `open-air/sgp41-module/libs/SGP30/SGP30-2.5K--3DModel-STEP-1.STEP` | 356403 | `7f6bd903ba6a5e4563336f1f0698f8b7c0835128e3e45361d0b8be8be01ba46e` |
| `open-air/sgp41-module/libs/SGP30/SGP30.kicad_mod` | 3230 | `85585614a65fddd2c0f5eed4cdd36db91d97d66e08e80eeb5427f0956a23f9d8` |
| `open-air/sgp41-module/libs/SGP30/SGP30.lib` | 763 | `5b27d3f116b1a580c73f132a58b39da6122cdde95ba602c94d0ef9e636d3e019` |
| `open-air/sgp41-module/libs/SGP30/how-to-import.htm` | 445 | `24e9a101a0ca11ff7db51062503d7e4ccdb70678f037eea9b38e7e61a762634f` |
| `open-air/sgp41-module/libs/SGP4X/SGP41-D-R4.lib` | 901 | `30a5213cc29419417cd572af7c11b7c43766d8f9d52c34b09d58d1d9be650c34` |
| `open-air/sgp41-module/libs/SGP4X/SGP41-D-R4.step` | 196038 | `2dfb3f2ad03b65f491d62aa5eed194c00c9300e7088b9958334683c0240d97b4` |
| `open-air/sgp41-module/libs/SGP4X/SGP4x.bak` | 73 | `247609451c32d19aaec2bc24eaf6a9e5f2d9dab36df573d812ac0508c611be9b` |
| `open-air/sgp41-module/libs/SGP4X/SGP4x.kicad_sym` | 2869 | `1ab5d0cc151a7a080a99d8c3cd01aebeae3f61fa11c0fe02d5da59ee596d035f` |
| `open-air/sgp41-module/libs/SGP4X/XDCR_SGP41-D-R4.kicad_mod` | 2416 | `573ca136db1193e81968bd805bb6f6fbf4a07b7f7ed389894bb70e8838a5319d` |
| `open-air/sgp41-module/libs/SGP4X.pretty/XDCR_SGP41-D-R4.kicad_mod` | 3706 | `bc5fc7d39f7a8ba714ac03119621c3edb4ae5eb1c5f956b919cc020f12cfea6b` |
| `open-air/sgp41-module/production/BOM/sgp41-bom.xls` | 27136 | `70d9c1079d47ee3748b9f3b0602de65e26917b93e2041e4ac7f5e2f64a11f167` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-B_Cu.gbl` | 10697 | `a0dafbe63e82c6a7b779961270adcf9c7c7e7a3cb6b39678323ad7296a3a6470` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-B_Mask.gbs` | 701 | `c1e4eb6c6d2fb22a2a9775ae997a1d1feda269f4fdb8dcbf8595dfc9b281d8e0` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-B_Paste.gbp` | 518 | `1da88c8566dd04d73dbe06d0150ef1a56bd3ec4bd068bee3d3e31b63afa8cb0a` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-B_Silkscreen.gbo` | 6589 | `ecb13b51e28d63686e4e6bb13a2ad181e44fb0b2f7c7c6ea8e34c6c674d41143` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-Edge_Cuts.gm1` | 989 | `57babe1190317e796a0a0f2ccb283bd5306e9becd721468c24c16208c2bc24d7` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-F_Cu.gtl` | 5229 | `e801a8322b653ee3ac57e67ce27d7db460cc50e62e79b3177caaf01e78371e3e` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-F_Mask.gts` | 2341 | `c506500d879da0d8a288bc72ac05cd4603d40fd2759104502c218f157f2b4c95` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-F_Paste.gtp` | 2158 | `a116b2cf9e5ce006077b95b864b21bd25edbfe6bf4933c807a78abd4bfbd76e4` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-F_Silkscreen.gto` | 26099 | `24c02bff9d5cfda9260cb2e38d5f9754ab02c27db661725fed0e158b39973b43` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-NPTH-drl_map.gbr` | 3008 | `658df4b98c4e7bca5095fae8ab627ff8d86df43526014eeb9a8e9c0c53852e06` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-NPTH.drl` | 291 | `b47c612d60abf2380ddc1dc57cb9e1abef937fb533869377936fe6bfcbb49e05` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-PTH-drl_map.gbr` | 18205 | `d30539878c4cebe6312a8008e91bd802b40d1efd2b5c9e382b41aa458fee3f1a` |
| `open-air/sgp41-module/production/gerber/tvoc-sensor-module-PTH.drl` | 520 | `826964fe458be36d436f0a01dcb42cbcef9b0209886644d37394d74631ea4e6b` |
| `open-air/sgp41-module/sgp41-tvoc-sensor-module.kicad_prl` | 1313 | `617a9a8f88f9c6b93c4b4f64daf8568a44be3b76ed76e282022c99d1b342947e` |
| `open-air/sgp41-module/sgp41-tvoc-sensor-module.kicad_pro` | 9411 | `d5e3dae523de219f300637c3012bb64c1fdee337ea1bc57cfc092be6df4223da` |
| `open-air/sgp41-module/sgp41-tvoc-sensor-module.kicad_sch` | 25975 | `4e83d53415cb73e07af3b7a4f4bef5360ad58fd755297fb789f341cc70639cb1` |
| `open-air/sgp41-module/sym-lib-table` | 336 | `19ba4ce1b05ad6afd048404663ff02b6467cf02a280ba5f33d5951720cea4ce4` |
| `open-air/sgp41-module/tvoc-sensor-module.kicad_pcb` | 72629 | `fa16a4b14c930ca732f0b786cac2818a0e807f0b8c9edfa4d2e68c51cebcbe30` |
| `open-air/sgp41-module/tvoc-sensor-module.kicad_prl` | 1308 | `021dc5e410bdd46d7b562bb9a1ca6938ccc66ca12a9b778fb0beb7135c818b4e` |
| `open-air/sgp41-module/tvoc-sensor-module.kicad_pro` | 8119 | `f7b3fe2813b42d8e67fed88b2e1810e22b1047951cba713998aa02e70b79cc68` |
