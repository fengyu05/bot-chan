import asyncio
import datetime
import os
import uuid
from typing import Optional

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    status as http_status,
    UploadFile,
)
from sqlalchemy.orm import Session

from fluctlight.audio.text_to_speech import get_text_to_speech
from fluctlight.database.connection import get_db
from fluctlight.database.models.character import (
    Character as DbCharacter,
)
from fluctlight.data_model.interface.character import (
    Character,
    CharacterRequest,
    EditCharacterRequest,
    DeleteCharacterRequest,
)
from fluctlight.agent_catalog.catalog_manager import CatalogManager
from fluctlight.web_server.auth import get_current_user

router = APIRouter()


MAX_FILE_UPLOADS = 5



@router.get("/status")
async def status():
    return {"status": "ok", "message": "RealChar is running smoothly!"}


@router.get("/characters")
async def characters(user=Depends(get_current_user)):
    def get_image_url(character: DbCharacter) -> str:
        if character.location == "repo" and character.author_name == "Eden":
            # TODO: new local storage service
            return f"http://localhost:3000/statics/{character.character_id}/{character.character_id}.jpg"

        if character.data and "avatar_filename" in character.data:
            return f"http://localhost:3000/{character.data['avatar_filename']}"
        return (
            f"http://localhost:3000/statics/{character.character_id}/{character.character_id}.jpg"
        )

    def get_audio_url(character: Character) -> str:
        if character.location == "repo" and character.author_name == "Eden":
            # TODO: new local storage service
            return f"http://localhost:3000/statics/{character.character_id}/{character.character_id}.mp3"
        else:
            return f"http://localhost:3000/{character.author_id}/{character.voice_id}.mp3"

    uid = user["uid"] if user else None
    catalog: CatalogManager = CatalogManager.get_instance()
    return [
        {
            "character_id": character.character_id,
            "name": character.name,
            "source": character.source,
            "voice_id": character.voice_id,
            "author_name": character.author_name,
            "audio_url": get_audio_url(character),
            "image_url": get_image_url(character),
            "tts": character.tts,
            "is_author": character.author_id == uid,
            "location": character.location,
        }
        for character in sorted(catalog.characters.values(), key=lambda c: c.order)
        if character.author_id == uid or character.visibility == "public"
    ]


@router.post("/uploadfile")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    # upload to local disk
    os.makedirs(f"/user_uploads/{user['uid']}/", exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    new_filename = (
        f"/user_uploads/{user['uid']}/"
        f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-"
        f"{uuid.uuid4()}{file_extension}"
    )
    # save
    async with aiofiles.open(new_filename, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    return {"filename": new_filename[1:], "content-type": file.content_type}


@router.post("/create_character")
async def create_character(
    character_request: CharacterRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character = DbCharacter(**character_request.dict())
    character.id = str(uuid.uuid4().hex)  # type: ignore
    character.background_text = character_request.background_text  # type: ignore
    character.author_id = user["uid"] if user else "unknown"
    now_time = datetime.datetime.now()
    character.created_at = now_time  # type: ignore
    character.updated_at = now_time  # type: ignore
    await asyncio.to_thread(character.save, db)


@router.post("/edit_character")
async def edit_character(
    edit_character_request: EditCharacterRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character_id = edit_character_request.id
    character = await asyncio.to_thread(
        db.query(DbCharacter).filter(DbCharacter.id == character_id).one
    )
    if not character:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )

    if character.author_id != user["uid"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to edit this character",
            headers={"WWW-Authenticate": "Bearer"},
        )
    character = DbCharacter(**edit_character_request.dict())
    character.updated_at = datetime.datetime.now()  # type: ignore
    db.merge(character)
    db.commit()


@router.post("/delete_character")
async def delete_character(
    delete_character_request: DeleteCharacterRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character_id = delete_character_request.character_id
    character = await asyncio.to_thread(
        db.query(DbCharacter).filter(DbCharacter.id == character_id).one
    )
    if not character:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )

    if character.author_id != user["uid"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to delete this character",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db.delete(character)
    db.commit()


@router.post("/generate_audio")
async def generate_audio(text: str, tts: Optional[str] = None, user=Depends(get_current_user)):
    if not isinstance(text, str) or text == "":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Text is empty",
        )
    try:
        tts_service = get_text_to_speech(tts)
    except NotImplementedError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Text to speech engine not found",
        )
    audio_bytes: bytes = await tts_service.generate_audio(text)

    file_extension = ".mp3"
    new_filename = (
        f"/user_uploads/{user['uid']}/"
        f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-"
        f"{uuid.uuid4()}{file_extension}"
    )

    async with aiofiles.open(new_filename, "wb") as buffer:
        await buffer.write(audio_bytes)

    return {"filename": new_filename[1:], "content-type": "audio/mpeg"}



@router.get("/get_character")
async def get_character(
    character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    character = await asyncio.to_thread(
        db.query(DbCharacter).filter(DbCharacter.id == character_id).one
    )
    if not character:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )
    if character.author_id != user["uid"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to access this character",
            headers={"WWW-Authenticate": "Bearer"},
        )
    character_json = character.to_dict()
    return character_json

