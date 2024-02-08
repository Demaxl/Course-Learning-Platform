
from rest_framework.test import APITestCase

STUDENT_TOKEN = ""

class CourseViewsTest(APITestCase):
    
    def createUsers(self):
        self.client.post('/auth/users/', {
            "username": "demaxl",
            "password": "Characters12345!",
            "type": "STUDENT"
        })
        self.client.post('/auth/users/', {
            "username": "Micheal",
            "password": "Characters12345!",
            "type": "INSTRUCTOR"
        })

        self.client.post('/auth/users/', {
            "username": "brian",
            "password": "Characters12345!",
            "type": "INSTRUCTOR"
        })

    def setCredentials(self, jwt=None):
        token = "JWT "
        if not jwt:
            token += self.studentJWT
        else:
            token += jwt

        self.client.credentials(HTTP_AUTHORIZATION=token)


    def setUp(self) -> None:
        self.createUsers()
        
        self.studentJWT = self.client.post('/auth/jwt/create', {
            "username":"demaxl", 
            "password":"Characters12345!"
            }).data['access']
        
        self.instructorJWT = self.client.post('/auth/jwt/create', {
            "username":"Micheal", 
            "password":"Characters12345!"
            }).data['access']
        
        self.instructor2JWT = self.client.post('/auth/jwt/create', {
            "username":"brian", 
            "password":"Characters12345!"
            }).data['access']
        
        self.setCredentials(self.instructorJWT)
        self.client.post("/api/courses", {
            "title": "Testing in django",
            "description": "This is a course that tests in django"
        })
        
        self.setCredentials()
        

    def testCourseCreate(self):
        self.setCredentials(self.studentJWT)
        r = self.client.post("/api/courses", {
            "title": "Testing in django",
            "description": "This is a course that tests in django"
        })
        self.assertEqual(r.status_code, 403)

        self.setCredentials(self.instructorJWT)
        r = self.client.post("/api/courses", {
            "title": "Testing in django 2",
            "description": "This is a course that tests in django"
        })

        self.assertEqual(r.status_code, 201)

    def testCourseEdit(self):
        self.setCredentials(self.instructorJWT)
        r = self.client.patch(
            "/api/courses/1", {"title": "Testing in django!!!!"})
        self.assertEqual(r.status_code, 200)

        self.setCredentials(self.instructor2JWT)
        r = self.client.patch("/api/courses/1", {"title": "Testing in django!!!!"})
        self.assertEqual(r.status_code, 403)
        # print(self.client.get("/api/courses").content)



class LessonViewsTest(CourseViewsTest):
    def setUp(self) -> None:
        super().setUp()
        self.setCredentials(self.instructorJWT)
        r = self.client.post("/api/courses/1/lessons", {
            "title": "This is a test lesson",
            "lesson": {
                "type": "READING",
                "content": "A Reading"
            }
        }, format='json')

    def testLessonCreate(self):
        # Student creating 
        self.setCredentials(self.studentJWT)
        r = self.client.post("/api/courses/1/lessons", {
            "title": "This is a test lesson",
            "lesson": {
                "type": "READING",
                "content": "A Reading"
            }
        }, format='json')
        self.assertEqual(r.status_code, 403)


        # Wrong instructors
        self.setCredentials(self.instructor2JWT)
        r = self.client.post("/api/courses/1/lessons", {
            "title": "This is a test lesson",
            "lesson": {
                "type": "READING",
                "content": "A Reading"
            }
        }, format='json')
        self.assertEqual(r.status_code, 403)

    def testLessonEdit(self):
        self.setCredentials(self.instructorJWT)
        r = self.client.post("/api/courses/1/lessons/1", {
            "title": "This is a test lesson",
            "lesson": {
                "type": "READING",
                "content": "A Reading"
            }
        }, format='json')

    def testLessonView(self):
        self.setCredentials(self.instructor2JWT)
        r = self.client.get("/api/courses/1/lessons/1")

        self.assertEqual(r.status_code, 403)