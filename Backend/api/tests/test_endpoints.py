
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
        
        self.setCredentials()
        

    def testCourseCreate(self):
        r = self.client.post("/api/courses", {
            "title": "Testing in django",
            "description": "This is a course that tests in django"
        })
        self.assertEqual(r.status_code, 403)

        self.setCredentials(self.instructorJWT)
        r = self.client.post("/api/courses", {
            "title": "Testing in django",
            "description": "This is a course that tests in django"
        })

        self.assertEqual(r.status_code, 201)

    def testCourseEdit(self):
        self.setCredentials(self.instructorJWT)
        self.client.post("/api/courses", {
            "title": "Testing in django",
            "description": "This is a course that tests in django"
        })
        r = self.client.patch(
            "/api/courses/1", {"title": "Testing in django!!!!"})
        self.assertEqual(r.status_code, 200)

        self.setCredentials(self.instructor2JWT)
        r = self.client.patch("/api/courses/1", {"title": "Testing in django!!!!"})
        self.assertEqual(r.status_code, 403)
