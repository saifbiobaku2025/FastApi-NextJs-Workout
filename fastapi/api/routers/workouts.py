from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload
from api.models import Workout
from api.deps import db_dependency, user_dependency

router = APIRouter(
    prefix='/workouts',
    tags=['workouts']
)

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass


@router.get('/all')  
def get_workouts(db: db_dependency, user: user_dependency):
    return db.query(Workout).options(joinedload(Workout.routines)).filter(
        Workout.user_id == user.get('id')  # ← only fetch own workouts
    ).all()

@router.get('/{workout_id}')
def get_workout(db: db_dependency, user: user_dependency, workout_id: int):
    workout = db.query(Workout).options(joinedload(Workout.routines)).filter(
        Workout.id == int(workout_id),
        Workout.user_id == user.get('id')  # ← only fetch own workouts
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail='Workout not found')
    return workout


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_workout(db: db_dependency, user: user_dependency, workout: WorkoutCreate):
    # ← removed redundant `if user is None` check; user_dependency already raises 401
    db_workout = Workout(**workout.model_dump(), user_id=user.get('id'))
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(db: db_dependency, user: user_dependency, workout_id: int):
    db_workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == user.get('id')  # ← only delete own workouts
    ).first()
    if not db_workout:
        raise HTTPException(status_code=404, detail='Workout not found')
    db.delete(db_workout)
    db.commit()