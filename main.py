from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import mysql.connector

app = FastAPI()

# UserData 모델을 업데이트하여 모든 필드를 포함
class UserData(BaseModel):
    accessToken: str
    refreshToken: Optional[str] = None
    expiresAt: Optional[str] = None
    tokenType: Optional[str] = None
    userId: str
    userEmail: Optional[str] = None
    userName: Optional[str] = None
    userGender: Optional[str] = None
    userBirthday: Optional[str] = None
    userBirthyear: Optional[str] = None


# DB 연결 설정 (user_db)
def get_user_db_connection():
    try:
        connection = mysql.connector.connect(
            host="rds-yedecos.czuw6k08iijt.ap-northeast-2.rds.amazonaws.com",  # AWS RDS 엔드포인트
            user="leon",
            password="----",  # 비밀번호 추가 필요
            database="user_db"  # 로그인 데이터를 위한 데이터베이스
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to the user database: {err}")
        raise HTTPException(status_code=500, detail="User database connection failed")


# DB 연결 설정 (yedecos_performance)
def get_performance_db_connection():
    try:
        connection = mysql.connector.connect(
            host="rds-yedecos.czuw6k08iijt.ap-northeast-2.rds.amazonaws.com",  # AWS RDS 엔드포인트
            user="leon",
            password="----",  # 비밀번호 추가 필요
            database="yedecos_performance"  # 공연 데이터를 위한 데이터베이스
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to the performance database: {err}")
        raise HTTPException(status_code=500, detail="Performance database connection failed")


# 사용자 정보를 데이터베이스에 저장하는 함수
def save_user_to_database(user_data: UserData):
    try:
        connection = get_user_db_connection()
        cursor = connection.cursor()

        # INSERT 쿼리, 이미 존재하는 경우 UPDATE
        query = """
        INSERT INTO user (userId, accessToken, refreshToken, expiresAt, tokenType, userEmail, userName, userGender, userBirthday, userBirthyear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            accessToken = VALUES(accessToken),
            refreshToken = VALUES(refreshToken),
            expiresAt = VALUES(expiresAt),
            tokenType = VALUES(tokenType),
            userEmail = VALUES(userEmail),
            userName = VALUES(userName),
            userGender = VALUES(userGender),
            userBirthday = VALUES(userBirthday),
            userBirthyear = VALUES(userBirthyear)
        """

        # 데이터를 튜플로 변환하여 쿼리에 전달
        data = (
            user_data.userId, user_data.accessToken, user_data.refreshToken,
            user_data.expiresAt, user_data.tokenType, user_data.userEmail,
            user_data.userName, user_data.userGender, user_data.userBirthday, user_data.userBirthyear
        )

        cursor.execute(query, data)
        connection.commit()

        # 연결 종료
        cursor.close()
        connection.close()

        print("User data saved successfully")

    except mysql.connector.Error as err:
        print(f"Error saving user data: {err}")
        raise HTTPException(status_code=500, detail="Failed to save user data")


# POST 요청으로 사용자 데이터를 받는 엔드포인트
@app.post("/")
async def login(user_data: UserData):
    print("Received login request")  # 요청을 받았음을 나타내는 출력
    try:
        # 받은 데이터를 처리 (예: 데이터베이스에 저장하거나 토큰 검증 등)
        print(f"Received user data: {user_data}")

        # 사용자 정보를 데이터베이스에 저장하는 로직 추가
        save_user_to_database(user_data)

        return {
            "message": "Login successful",
            "userId": user_data.userId,
            "accessToken": user_data.accessToken,
            "refreshToken": user_data.refreshToken,
            "expiresAt": user_data.expiresAt,
            "tokenType": user_data.tokenType,
            "userEmail": user_data.userEmail,
            "userName": user_data.userName,
            "userGender": user_data.userGender,
            "userBirthday": user_data.userBirthday,
            "userBirthyear": user_data.userBirthyear,
        }
    except Exception as e:
        print(f"Error processing login request: {str(e)}")  # 에러 발생 시 출력
        raise HTTPException(status_code=400, detail=str(e))


# 공연 데이터를 위한 모델 정의
class Performance(BaseModel):
    prfnm: str  # 공연명
    genrenm: str  # 장르
    prfruntime: str  # 런타임
    fcltynm: str  # 공연장명
    district_code: int  # 지역코드
    poster: str  # 포스터 URL 추가


@app.get("/performances", response_model=List[Performance])
async def get_performances():
    try:
        connection = get_performance_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 포스터 URL도 함께 가져오는 쿼리
        query = """
        SELECT prfnm, genrenm, prfruntime, fcltynm, district_code, poster
        FROM Busan_kopis_performance_db
        """
        cursor.execute(query)
        performances = cursor.fetchall()

        # 공연 데이터 개수 출력
        print(f"Number of performances fetched: {len(performances)}")

        # 연결 종료
        cursor.close()
        connection.close()

        if not performances:
            raise HTTPException(status_code=404, detail="No performances found")

        return performances

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Failed to fetch performances")
    except Exception as e:
        print(f"Error fetching performances: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch performances")


# 모든 요청을 로그로 기록하는 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Received request: {request.method} {request.url}")  # 모든 요청에 대한 로그
    response = await call_next(request)
    return response


if __name__ == "__main__":
    print("Starting FastAPI server...")  # 서버 시작 시 출력
    uvicorn.run(app, host="127.0.0.1", port=8000)
    print("FastAPI server is running")  # 서버 실행 중 출력
