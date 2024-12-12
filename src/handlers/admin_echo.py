from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.admin_crud as crud

import src.keyboards.kb as kb

router_main: Router = Router()