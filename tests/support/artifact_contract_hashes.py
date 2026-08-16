"""Fixed SHA-256 expectations for artifact contract characterization."""

SCHEMA_HASHES = {
    "SCHEMA_VERSION": "b05e244762b1e472be89a93800cc3ee326743cecb55984bf12813addb8de66d0",
    "DEFAULT_TIMEZONE": "767f41f547937e73856a64ae5abc126fab75c2fe4fa6161c59de416a8419cc73",
    "SCHEMA_DECLARATION": "775d4ffdba6a5c5aaa17462473af2201a3e3ac9a2c3758c8e8804815d2a5eaad",
    "SCHEMA_CONFIG": "3caf13e6de1913fbb6aff074c215611bf730184481c680f4d176f3a8d59e022b",
    "SCHEMA_LOG": "7b52d6ce43caa59e24e26f500b3199c6ab16f22b376a8a04fa2f0817274728b3",
    "SCHEMA_RESULT": "9d706d485c16033b0d62b1eb221e65b852168745dfa88a1b9a491a229ee1782e",
    "LINKS_REMARK": "ac09408f8e04aaee502523a06ba49fec1dbeb5beaa9d13a294e9241920d1d7b2",
}
OBJECT_HASHES = [
    "01ab9bf121d11c06bacaf9db589a793282b171324c2dff9395a8b4740bf54cd0",
    "d9cf2e523fb5faf6b5d08d9c2fe5908baf3938bb194178ac7924042dd8e51311",
    "4c6dee80696990886cd6fc888e891776518f5135ca80d950fd6c9eedb0d00112",
    "a84671f01acd8fc7e75ea41127f436f6fe5826eef4bca83dcaaa04cca1cbceee",
]
PRETTY_HASHES = [
    "bcddd47dce7dba55880f67f85ff79d02f080f198890edece359902659cdd0d03",
    "c0b0afcba1e62370c3d5624b3671e825f8aa5967f40ee3fda8322f081dd24881",
    "c004244f2933eddb252b783f5f4e776264b4e1abdd9f27c6b5c7dd768a97eca1",
    "4e9012aa5d6bc078bf367fd8d140644c3cf01f157a1435be26975ebf1f208164",
]
REFERENCE_FILES = [
    ("declaration_game.json", PRETTY_HASHES[0]),
    ("config_game_g01.json", PRETTY_HASHES[1]),
    ("log_game_g01.json", PRETTY_HASHES[2]),
    ("result_game.json", PRETTY_HASHES[3]),
]
LOCAL_FILES = [
    ("declaration_game.json", "71d2edca2b6f239bdba387c7fe3348ee66be702421670608fcd5a5e1c28f47e8"),
    ("config_game_g01.json", "66e1743da003d1636d160b4ade9bf25a7b6f1046478de483bd6c9ca4c6dd5184"),
    ("log_game_g01.json", "e933c34bc23c39d19b56988ff04b10bebdbb33619d7fa2d9108969c1771b8a47"),
    ("result_game.json", "e67a41ef2f45ecd3bece62a63c4748d0fd1f52ac6f8449648fc04d390d36233f"),
]
