from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List, Optional
import json
from datetime import datetime
from models.session import Session as PydanticSession
from models.lap import Lap as PydanticLap
from models.telemetry import TelemetrySample

Base = declarative_base()

class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String)          # <-- missing, add this
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
    samples = Column(JSON) # On garde les samples en JSON pour le moment

    session = relationship("SessionDB", back_populates="laps")

class SQLiteStorage:
    def __init__(self, db_url="sqlite:///./telemetry.db"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self._migrate_session_vehicle_columns()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _migrate_session_vehicle_columns(self):
        columns = {
            column["name"] for column in inspect(self.engine).get_columns("sessions")
        }
        missing = {
            "car_code": "INTEGER",
            "car_name": "VARCHAR",
            "manufacturer_id": "INTEGER",
        }
        with self.engine.begin() as connection:
            for name, sql_type in missing.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE sessions ADD COLUMN {name} {sql_type}"))

    def save_session(self, session: PydanticSession) -> int:
        db = self.SessionLocal()
        db_session = SessionDB(
            driver_id=session.driver_id,
            car_code=session.car_code,
            car_name=session.car_name,
            manufacturer_id=session.manufacturer_id,
            start_time=session.start_time,
            end_time=session.end_time
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        session_id = db_session.id
        db.close()
        return session_id

    def update_session(self, session: PydanticSession):
        db = self.SessionLocal()
        db_session = db.query(SessionDB).filter(SessionDB.id == session.id).first()
        if db_session:
            db_session.end_time = session.end_time
            db_session.car_code = session.car_code
            db_session.car_name = session.car_name
            db_session.manufacturer_id = session.manufacturer_id
            db.commit()
        db.close()

    def save_lap(self, lap: PydanticLap) -> int:
        db = self.SessionLocal()
        samples_dict = [sample.model_dump() for sample in lap.samples]
        
        db_lap = LapDB(
            session_id=lap.session_id,
            lap_number=lap.lap_number,
            lap_time=lap.lap_time,
            valid=lap.valid,
            samples_count=lap.samples_count,
            samples=samples_dict
        )
        db.add(db_lap)
        db.commit()
        db.refresh(db_lap)
        lap_id = db_lap.id
        db.close()
        return lap_id

    def get_session(self, session_id: int) -> Optional[PydanticSession]:
        db = self.SessionLocal()
        db_session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
        if not db_session:
            db.close()
            return None
            
        laps = []
        for db_lap in db_session.laps:
            samples = [TelemetrySample(**s) for s in db_lap.samples]
            laps.append(PydanticLap(
                id=db_lap.id,
                session_id=db_lap.session_id,
                lap_number=db_lap.lap_number,
                lap_time=db_lap.lap_time,
                valid=db_lap.valid,
                samples_count=db_lap.samples_count,
                samples=samples
            ))
        
        session = PydanticSession(
            id=db_session.id,
            driver_id=db_session.driver_id,
            car_code=db_session.car_code,
            car_name=db_session.car_name,
            manufacturer_id=db_session.manufacturer_id,
            start_time=db_session.start_time,
            end_time=db_session.end_time,
            laps=laps
        )
        db.close()
        return session

    def close(self):
        self.engine.dispose()
