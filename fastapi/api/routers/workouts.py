from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import db_dependency, user_dependency
from api.models import Workout
from api.schemas import WorkoutCreate, WorkoutRead

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
)


def _workouts_for_user(db: Session, user_id: int) -> List[Workout]:
    return db.query(Workout).filter(Workout.user_id == user_id).all()


@router.get("/workouts", response_model=List[WorkoutRead])
def get_workouts(db: db_dependency, user: user_dependency):
    return _workouts_for_user(db, user["id"])


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(db: db_dependency, user: user_dependency, workout_id: int):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == user["id"],
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=WorkoutRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_workout(db: db_dependency, user: user_dependency, workout: WorkoutCreate):
    db_workout = Workout(**workout.model_dump(), user_id=user["id"])
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(db: db_dependency, user: user_dependency, workout_id: int):
    db_workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == user["id"],
    ).first()
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(db_workout)
    db.commit()
