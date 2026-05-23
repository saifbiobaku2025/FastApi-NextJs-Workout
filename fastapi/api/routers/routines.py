from pydantic import BaseModel
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload
from api.models import Routine, Workout
from api.deps import db_dependency, user_dependency

router = APIRouter(
    prefix='/routines',
    tags=['routines']
)


class RoutineBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoutineCreate(RoutineBase):
    workout_ids: List[int] = []  # ← was List[list], should be list of ints


@router.get('/')
def get_routines(db: db_dependency, user: user_dependency):
    # ← filter must be outside joinedload, joinedload only takes the relationship
    return db.query(Routine).options(joinedload(Routine.workouts)).filter(
        Routine.user_id == user.get('id')
    ).all()


@router.get('/{routine_id}')
def get_routine(db: db_dependency, user: user_dependency, routine_id: int):
    routine = db.query(Routine).options(joinedload(Routine.workouts)).filter(
        Routine.id == routine_id,
        Routine.user_id == user.get('id')
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail='Routine not found')
    return routine


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_routine(db: db_dependency, user: user_dependency, routine: RoutineCreate):
    db_routine = Routine(
        name=routine.name, description=routine.description, user_id=user.get('id'))

    # ← was Routine.Workout (wrong model/case)
    for workout_id in routine.workout_ids:
        # ← was shadowing Workout class with variable
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if workout:
            db_routine.workouts.append(workout)

    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)

    # ← reload with joinedload so workouts are included in response
    db_routine = db.query(Routine).options(joinedload(Routine.workouts)).filter(
        Routine.id == db_routine.id
    ).first()
    return db_routine


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(db: db_dependency, user: user_dependency, routine_id: int):
    db_routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == user.get('id')  # ← only delete own routines
    ).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail='Routine not found')
    db.delete(db_routine)
    db.commit()
