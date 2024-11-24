from fluctlight.data_model.slack import FileObject


def test_create_file_object():
    file_payload = {
        "id": "F07BYSPHHMM",
        "created": 1721007504,
        "timestamp": 1721007504,
        "name": "audio_message.webm",
        "title": "audio_message.webm",
        "mimetype": "video/quicktime",
        "filetype": "mov",
        "pretty_type": "QuickTime Movie",
        "user": "U0502429A8N",
        "user_team": "T050B663C4C",
        "editable": False,
        "size": 43485,
        "mode": "hosted",
        "is_external": False,
        "external_type": "",
        "is_public": False,
        "public_url_shared": False,
        "display_as_bot": False,
        "username": "",
        "subtype": "slack_audio",
        "transcription": {"status": "processing"},
        "url_private": "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/audio_message_audio.mp4",
        "url_private_download": "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/download/audio_message_audio.mp4",
        "duration_ms": 2600,
        "aac": "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/audio_message_audio.mp4",
        "audio_wave_samples": [
            36,
            21,
            29,
            29,
            42,
            23,
            17,
            13,
            19,
            29,
            13,
            22,
            30,
            21,
            24,
            15,
            9,
            10,
            10,
            10,
            12,
            11,
            8,
            9,
            9,
            16,
            8,
            11,
            9,
            12,
            13,
            9,
            11,
            19,
            14,
            18,
            48,
            24,
            36,
            88,
            76,
            65,
            61,
            50,
            22,
            12,
            21,
            54,
            28,
            9,
            4,
            11,
            15,
            9,
            11,
            26,
            48,
            84,
            84,
            87,
            90,
            94,
            95,
            94,
            98,
            100,
            94,
            93,
            98,
            95,
            89,
            88,
            58,
            57,
            24,
            14,
            9,
            4,
            4,
            4,
            4,
            3,
            4,
            6,
            3,
            2,
            4,
            4,
            6,
            5,
            12,
            7,
            3,
            2,
            3,
            3,
            3,
            2,
            3,
            2,
        ],
        "media_display_type": "audio",
        "permalink": "https://hyperspace-tech.slack.com/files/U0502429A8N/F07BYSPHHMM/audio_message.webm",
        "permalink_public": "https://slack-files.com/T050B663C4C-F07BYSPHHMM-862af09b80",
        "has_rich_preview": False,
        "file_access": "visible",
    }

    file_object = FileObject(**file_payload)
    assert file_object.id == "F07BYSPHHMM"
    assert file_object.created == 1721007504
    assert file_object.timestamp == 1721007504
    assert file_object.name == "audio_message.webm"
    assert file_object.title == "audio_message.webm"
    assert file_object.mimetype == "video/quicktime"
    assert file_object.filetype == "mov"
    assert file_object.pretty_type == "QuickTime Movie"
    assert file_object.user == "U0502429A8N"
    assert file_object.user_team == "T050B663C4C"
    assert file_object.editable == False
    assert file_object.size == 43485
    assert file_object.mode == "hosted"
    assert file_object.is_external == False
    assert file_object.external_type == ""
    assert file_object.is_public == False
    assert file_object.public_url_shared == False
    assert file_object.display_as_bot == False
    assert file_object.username == ""
    assert file_object.subtype == "slack_audio"
    assert file_object.transcription.status == "processing"
    assert file_object.transcription.preview == None
    assert (
        file_object.url_private
        == "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/audio_message_audio.mp4"
    )
    assert (
        file_object.url_private_download
        == "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/download/audio_message_audio.mp4"
    )
    assert file_object.duration_ms == 2600
    assert (
        file_object.aac
        == "https://files.slack.com/files-tmb/T050B663C4C-F07BYSPHHMM-4907f4fdaf/audio_message_audio.mp4"
    )
    assert file_object.audio_wave_samples == [
        36,
        21,
        29,
        29,
        42,
        23,
        17,
        13,
        19,
        29,
        13,
        22,
        30,
        21,
        24,
        15,
        9,
        10,
        10,
        10,
        12,
        11,
        8,
        9,
        9,
        16,
        8,
        11,
        9,
        12,
        13,
        9,
        11,
        19,
        14,
        18,
        48,
        24,
        36,
        88,
        76,
        65,
        61,
        50,
        22,
        12,
        21,
        54,
        28,
        9,
        4,
        11,
        15,
        9,
        11,
        26,
        48,
        84,
        84,
        87,
        90,
        94,
        95,
        94,
        98,
        100,
        94,
        93,
        98,
        95,
        89,
        88,
        58,
        57,
        24,
        14,
        9,
        4,
        4,
        4,
        4,
        3,
        4,
        6,
        3,
        2,
        4,
        4,
        6,
        5,
        12,
        7,
        3,
        2,
        3,
        3,
        3,
        2,
        3,
        2,
    ]
    assert file_object.media_display_type == "audio"
    assert (
        file_object.permalink
        == "https://hyperspace-tech.slack.com/files/U0502429A8N/F07BYSPHHMM/audio_message.webm"
    )
    assert (
        file_object.permalink_public
        == "https://slack-files.com/T050B663C4C-F07BYSPHHMM-862af09b80"
    )
    assert file_object.has_rich_preview == False
    assert file_object.file_access == "visible"
