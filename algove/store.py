from datetime import datetime
from typing import Any, TypeVar, Type, Callable, List
import logging
from typing_extensions import Annotated
from sqlalchemy import create_engine, select, ForeignKey, Column, Table, JSON
import enum
from getpass import getuser
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy import func

from traceback import format_exc
from inspect import signature
from hashlib import sha1
import json


import random

from sqlalchemy.orm import (
    relationship,
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
)

logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}

    # def __repr__(self):
    #     vals = {k: v for k, v in self.__dict__.items() if not k.startswith("_sa")}
    #     vals_str = ", ".join(f"{k}={v}" for k, v in vals.items())
    #     type_name = type(self).__name__
    #     return f"{type_name}({vals_str})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    @staticmethod
    def default() -> "User":
        return User(name=getuser())


class AlgoType(enum.Enum):
    CLASSIFICATION = "clf"
    REGRESSION = "reg"


class Level(enum.Enum):
    NO_IMPACT = "no"
    LOW = "low"
    MEDIUM = "med"
    HIGH = "high"


class Algorithm(Base):
    __tablename__ = "algorithm"

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str]
    type: Mapped[AlgoType]
    level: Mapped[Level]
    models: Mapped[List["Model"]] = relationship(back_populates="algorithm")


class ModelStatus(enum.Enum):
    DEV = "dev"
    STAGING = "stage"
    PROD = "prod"
    DEPRECATED = "dep"
    RETIRED = "ret"


model_experiment_table = Table(
    "model_experiment",
    Base.metadata,
    Column("model_id", ForeignKey("model.id"), primary_key=True),
    Column("experiment_id", ForeignKey("experiment.id"), primary_key=True),
)


class Model(Base):
    __tablename__ = "model"

    id: Mapped[int] = mapped_column(primary_key=True)
    algorithm_name = mapped_column(ForeignKey("algorithm.name"), nullable=False)
    algorithm: Mapped["Algorithm"] = relationship(back_populates="models")
    name: Mapped[str]
    status: Mapped[ModelStatus]
    description: Mapped[str]
    created_at: Mapped[timestamp]
    experiments: Mapped[List["Experiment"]] = relationship(
        secondary=model_experiment_table, back_populates="models"
    )


class Experiment(Base):
    __tablename__ = "experiment"

    id: Mapped[str] = mapped_column(primary_key=True)
    models: Mapped[List[Model]] = relationship(
        secondary=model_experiment_table, back_populates="experiments"
    )
    description: Mapped[str]
    created_at: Mapped[timestamp]
    runs: Mapped[List["Run"]] = relationship(back_populates="experiment")


class RunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    RETYRING = "RETRYING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    def finished(self) -> bool:
        return self in (RunStatus.SUCCESS, RunStatus.FAILED)


class Run(Base):
    __tablename__ = "runs"
    # id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id = mapped_column(
        ForeignKey("experiment.id"), nullable=False, primary_key=True
    )
    input_hash: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    experiment: Mapped[Experiment] = relationship(back_populates="runs")
    status: Mapped[RunStatus]
    created_at: Mapped[timestamp]
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    # TODO: make this better
    inputs: Mapped[dict[str, Any]]
    outputs: Mapped[dict[str, Any]] = mapped_column(nullable=True)
    error_msg: Mapped[str] = mapped_column(nullable=True)


T = TypeVar("T", bound=Base)


def get_or(
    sess: Session, key: str, val: Any, table: Type[T], factory: Callable[[], T]
) -> T:
    result = sess.execute(select(table).filter_by(**{key: val})).scalar_one_or_none()
    if result is None:
        result = factory()
        logger.info(f"Creating {table.__name__} {key} = {val}")
        sess.add(result)
    else:
        logger.info(f"Found {table.__name__} {key} = {val}")
    return result


def to_enum(t, val):
    if isinstance(val, t):
        return val
    else:
        try:
            return t(val)
        except ValueError:
            expects = [level.value for level in t]
            msg = f"'{val}' is not a valid {t.__name__}, expected one of: {expects}"
            raise ValueError(msg)


def get_user(sess, name: str):
    return get_or(sess, "name", name, User, lambda: User(name=name))


def get_algo(
    sess, name: str, description: str, type: AlgoType | str, level: Level | str
):
    return get_or(
        sess,
        "name",
        name,
        Algorithm,
        lambda: Algorithm(
            name=name,
            description=description,
            type=to_enum(AlgoType, type),
            level=to_enum(Level, level),
        ),
    )


def get_model(
    sess,
    name: str,
    algorithm: Algorithm,
    status: ModelStatus | str = "dev",
    description: str = "",
):
    return get_or(
        sess,
        "name",
        name,
        Model,
        lambda: Model(
            name=name,
            status=to_enum(ModelStatus, status),
            description=description,
            algorithm_name=algorithm.name,
        ),
    )


def get_experiment(
    sess, name: str, description: str, models: List[Model]
) -> Experiment:
    return get_or(
        sess,
        "id",
        name,
        Experiment,
        lambda: Experiment(id=name, description=description, models=models),
    )


def get_run(sess, exp_id: str, params: dict[str, Any]) -> Run:
    hashed = hash_dict(params)
    run = sess.execute(
        select(Run).filter_by(experiment_id=exp_id, input_hash=hashed)
    ).scalar_one_or_none()
    if run is None:
        exp = sess.execute(select(Experiment).filter_by(id=exp_id)).scalar_one()
        run = Run(
            experiment=exp, input_hash=hashed, inputs=params, status=RunStatus.PENDING
        )
        sess.add(run)
    return run  # type: ignore


engine = create_engine("sqlite+pysqlite:///algove.sqlite")
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
sess = Session(engine)


def hash_dict(d: dict[str, Any]) -> str:
    return sha1((json.dumps(sorted(d.items()))).encode()).hexdigest()


logging.basicConfig()
logger.setLevel("INFO")

with sess.begin():
    user = get_user(sess, "Evan")
    algo = get_algo(sess, "Classifier", "Classifies the thing", type="clf", level="no")
    model = get_model(sess, "LinearRegression", algo)
    exp1 = get_experiment(sess, "my_exp", "hi am an experiment", models=[model])
    exp2 = get_experiment(sess, "my_exp_2", "Hi am another experiment", models=[model])
    exp_id = exp2.id


def run_deco(sess, experiment_id: str):
    def wrapper(f):
        sig = signature(f)

        def wrapped(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = bound.arguments

            with sess.begin():
                run: Run = get_run(  # type: ignore
                    sess, exp_id=experiment_id, params=dict(params)
                )

                # Early exit
                if run.status.finished():
                    logger.info(f"Run {run.status}, no computation necessary")
                    return run.outputs
                logger.info(f"Run not finished: {params}")

                try:
                    result = f(*args, **kwargs)
                    run.outputs = result
                    run.status = RunStatus.SUCCESS
                    run.completed_at = datetime.utcnow()
                    return result
                except Exception:
                    run.error_msg = format_exc()
                    run.outputs = None
                    run.status = RunStatus.FAILED

        return wrapped

    return wrapper


@run_deco(sess, experiment_id=exp_id)
def my_func(a: int) -> dict[str, Any]:
    if random.random() > 0.7:
        raise ValueError("Lol heisenbug")

    return {"loss": 1.0 - a / 10, "recall": 0.1 * a}


for i in range(10):
    my_func(i)


with sess.begin():
    best_runs = sess.execute(select(Run).order_by(Run.outputs["loss"])).first()
    if best_runs is not None:
        best = best_runs[0]
        print("Best run is:", best.inputs, best.outputs, best.completed_at)
