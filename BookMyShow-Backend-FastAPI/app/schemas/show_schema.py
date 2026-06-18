from pydantic import BaseModel, ConfigDict
from datetime import time, date
from app.constants.enums import FormatEnum

######### SHOW SCHEDULE - movie #########
class ShowSchedules(BaseModel):
    movie_id : str
    screen_id : int
    venue_id: int

class ShowScheduleCreate(ShowSchedules):
    pass

class ShowScheduleRead(ShowSchedules):
    schedule_id : int
    model_config=ConfigDict(from_attributes=True)
    
######### SHOW TIMINGS #########
class ShowScheduleTimings(BaseModel):
    schedule_id : int
    language : str
    format : FormatEnum
    show_date : date
    show_time : time
    is_active : bool =True
    is_completed : bool = False

class ShowTimingCreate(ShowScheduleTimings):
    pass 

class ShowTimingRead(ShowScheduleTimings):
    show_id : int
    model_config=ConfigDict(from_attributes=True)