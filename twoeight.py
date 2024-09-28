from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import List

# FastAPI instance
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./courses.db"  # SQLite database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model for the Course
class CourseDB(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for the API requests/responses
class Course(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True

# POST: Add a new software course
@app.post("/courses/", response_model=Course)
async def add_course(course: Course, db: Session = Depends(get_db)):
    db_course = CourseDB(id=course.id, name=course.name, description=course.description)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# GET: Retrieve the list of all courses
@app.get("/courses/", response_model=List[Course])
async def get_courses(db: Session = Depends(get_db)):
    return db.query(CourseDB).all()

# Exception handling for duplicate courses (optional)
@app.post("/courses/unique/", response_model=Course)
async def add_unique_course(course: Course, db: Session = Depends(get_db)):
    existing_course = db.query(CourseDB).filter(CourseDB.id == course.id).first()
    if existing_course:
        raise HTTPException(status_code=400, detail="Course with this ID already exists.")
    db_course = CourseDB(id=course.id, name=course.name, description=course.description)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

