from pathlib import Path
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    inspect,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from models.session import Session as PydanticSession
from models.lap import Lap as PydanticLap
from models.telemetry import TelemetrySample


Base = declarative_base()


# sqlite.py is located at:
# gt7-telemetry/telemetry_engine/storage/sqlite.py
#
# parents[0] -> storage/
# parents[1] -> telemetry_engine/
# parents[2] -> gt7-telemetry/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "telemetry.db"


class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String)
    car_code = Column(Integer, nullable=True)
    car_name = Column(String, nullable=True)
    manufacturer_id = Column(Integer, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)

    laps = relationship("LapDB", back_populates="session")


class LapDB(Base):
    __tablename__ = "laps"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    lap_number = Column(Integer)
    lap_time = Column(Float, nullable=True)
    valid = Column(Boolean, default=True)
    samples_count = Column(Integer, default=0)
    samples = Column(JSON)

    session = relationship("SessionDB", back_populates="laps")


class SQLiteStorage:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = f"sqlite:///{DATABASE_PATH}"

        print(f"Using database: {DATABASE_PATH}")

        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )

        Base.metadata.create_all(bind=self.engine)

        self._migrate_session_vehicle_columns()

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def _migrate_session_vehicle_columns(self):
        columns = {
            column["name"]
            for column in inspect(self.engine).get_columns("sessions")
        }

        missing = {
            "car_code": "INTEGER",
            "car_name": "VARCHAR",
            "manufacturer_id": "INTEGER",
        }

        with self.engine.begin() as connection:
            for name, sql_type in missing.items():
                if name not in columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE sessions "
                            f"ADD COLUMN {name} {sql_type}"
                        )
                    )

    def save_session(self, session: PydanticSession) -> int:
        db = self.SessionLocal()

        db_session = SessionDB(
            driver_id=session.driver_id,
            car_code=session.car_code,
            car_name=session.car_name,
            manufacturer_id=session.manufacturer_id,
            start_time=session.start_time,
            end_time=session.end_time,
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        session_id = db_session.id

        db.close()

        return session_id

    def update_session(self, session: PydanticSession):
        db = self.SessionLocal()

        db_session = (
            db.query(SessionDB)
            .filter(SessionDB.id == session.id)
            .first()
        )

        if db_session:
            db_session.end_time = session.end_time
            db_session.car_code = session.car_code
            db_session.car_name = session.car_name
            db_session.manufacturer_id = session.manufacturer_id

            db.commit()

        db.close()

    def save_lap(self, lap: PydanticLap) -> int:
        db = self.SessionLocal()

        samples_dict = [
            sample.model_dump()
            for sample in lap.samples
        ]

        db_lap = LapDB(
            session_id=lap.session_id,
            lap_number=lap.lap_number,
            lap_time=lap.lap_time,
            valid=lap.valid,
            samples_count=lap.samples_count,
            samples=samples_dict,
        )

        db.add(db_lap)
        db.commit()
        db.refresh(db_lap)

        lap_id = db_lap.id

        db.close()

        return lap_id

    def get_sessions(self) -> list[PydanticSession]:
        db = self.SessionLocal()

        db_sessions = db.query(SessionDB).all()

        sessions = []

        for db_session in db_sessions:
            laps = []

            for db_lap in db_session.laps:
                samples = [
                    TelemetrySample(**sample)
                    for sample in (db_lap.samples or [])
                ]

                laps.append(
                    PydanticLap(
                        id=db_lap.id,
                        session_id=db_lap.session_id,
                        lap_number=db_lap.lap_number,
                        lap_time=db_lap.lap_time,
                        valid=db_lap.valid,
                        samples_count=db_lap.samples_count,
                        samples=samples,
                    )
                )

            sessions.append(
                PydanticSession(
                    id=db_session.id,
                    driver_id=db_session.driver_id,
                    car_code=db_session.car_code,
                    car_name=db_session.car_name,
                    manufacturer_id=db_session.manufacturer_id,
                    start_time=db_session.start_time,
                    end_time=db_session.end_time,
                    laps=laps,
                )
            )

        db.close()

        return sessions
    
    def get_session(
        self,
        session_id: int,
    ) -> Optional[PydanticSession]:
        db = self.SessionLocal()

        print(f"Fetching session with ID: {session_id}")
        print(f"Using database: {DATABASE_PATH}")

        db_session = (
            db.query(SessionDB)
            .filter(SessionDB.id == session_id)
            .first()
        )

        if not db_session:
            print(f"Session {session_id} not found")
            db.close()
            return None

        laps = []

        for db_lap in db_session.laps:
            samples = [
                TelemetrySample(**sample)
                for sample in (db_lap.samples or [])
            ]

            laps.append(
                PydanticLap(
                    id=db_lap.id,
                    session_id=db_lap.session_id,
                    lap_number=db_lap.lap_number,
                    lap_time=db_lap.lap_time,
                    valid=db_lap.valid,
                    samples_count=db_lap.samples_count,
                    samples=samples,
                )
            )

        session = PydanticSession(
            id=db_session.id,
            driver_id=db_session.driver_id,
            car_code=db_session.car_code,
            car_name=db_session.car_name,
            manufacturer_id=db_session.manufacturer_id,
            start_time=db_session.start_time,
            end_time=db_session.end_time,
            laps=laps,
        )

        db.close()

        return session

    def get_laps(self) -> list[PydanticLap]:
        db = self.SessionLocal()

        db_laps = db.query(LapDB).all()

        laps = []

        for db_lap in db_laps:
            samples = [
                TelemetrySample(**sample)
                for sample in (db_lap.samples or [])
            ]

            laps.append(
                PydanticLap(
                    id=db_lap.id,
                    session_id=db_lap.session_id,
                    lap_number=db_lap.lap_number,
                    lap_time=db_lap.lap_time,
                    valid=db_lap.valid,
                    samples_count=db_lap.samples_count,
                    samples=samples,
                )
            )

        db.close()

        return laps

    def get_lap(self, lap_id: int) -> Optional[PydanticLap]:
        db = self.SessionLocal()

        db_lap = (
            db.query(LapDB)
            .filter(LapDB.id == lap_id)
            .first()
        )

        if not db_lap:
            db.close()
            print(f"Lap {lap_id} not found")
            return None

        samples = [
            TelemetrySample(**sample)
            for sample in (db_lap.samples or [])
        ]

        lap = PydanticLap(
            id=db_lap.id,
            session_id=db_lap.session_id,
            lap_number=db_lap.lap_number,
            lap_time=db_lap.lap_time,
            valid=db_lap.valid,
            samples_count=db_lap.samples_count,
            samples=samples,
        )

        db.close()

        return lap

    def close(self):
        self.engine.dispose()