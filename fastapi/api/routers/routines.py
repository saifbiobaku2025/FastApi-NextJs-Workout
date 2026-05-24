from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload, Session

from api.deps import db_dependency, user_dependency
from api.models import Routine, Workout
from api.schemas import RoutineCreate, RoutineRead

router = APIRouter(
    prefix="/routines",
    tags=["routines"],
)


def _routines_for_user(db: Session, user_id: int) -> List[Routine]:
    return (
        db.query(Routine)
        .options(joinedload(Routine.workouts))
        .filter(Routine.user_id == user_id)
        .all()
    )


@router.get("", response_model=List[RoutineRead])
@router.get("/", response_model=List[RoutineRead], include_in_schema=False)
def get_routines(db: db_dependency, user: user_dependency):
    return _routines_for_user(db, user["id"])


@router.get("/{routine_id}", response_model=RoutineRead)
def get_routine(db: db_dependency, user: user_dependency, routine_id: int):
    routine = (
        db.query(Routine)
        .options(joinedload(Routine.workouts))
        .filter(Routine.id == routine_id, Routine.user_id == user["id"])
        .first()
    )
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return routine


@router.post("", response_model=RoutineRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=RoutineRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_routine(db: db_dependency, user: user_dependency, routine: RoutineCreate):
    db_routine = Routine(
        name=routine.name,
        description=routine.description,
        user_id=user["id"],
    )

    for workout_id in routine.workouts:
        workout = db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user["id"],
        ).first()
        if workout:
            db_routine.workouts.append(workout)

    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)

    loaded = (
        db.query(Routine)
        .options(joinedload(Routine.workouts))
        .filter(Routine.id == db_routine.id)
        .first()
    )
    return loaded


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(db: db_dependency, user: user_dependency, routine_id: int):
    db_routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == user["id"],
    ).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    db.delete(db_routine)
    db.commit()
