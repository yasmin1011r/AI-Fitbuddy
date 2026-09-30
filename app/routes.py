from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


@router.post("/generate-workout")
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: str = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    print("generate workout route called")

    existing_user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": existing_user,
                "workout_plan": existing_user.original_plan,
                "nutrition_tip": existing_user.nutrition_tip,
                "message": "Your existing plan was loaded successfully."
            }
        )

    workout_plan = generate_workout_gemini(
        name,
        age,
        weight,
        goal,
        intensity
    )

    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    user = User(
        user_id=user_id,
        name=name,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "user": user,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "message": "7-Day Plan generated successfully!"
        }
    )


@router.post("/submit-feedback")
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": "User ID not found."
            }
        )

    updated_plan = update_workout_plan(
        user.original_plan,
        feedback
    )

    user.feedback = feedback
    user.updated_plan = updated_plan

    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "user": user,
            "workout_plan": updated_plan,
            "nutrition_tip": user.nutrition_tip,
            "message": "Workout plan updated successfully!"
        }
    )


@router.get("/view-all-users")
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users
        }
    )