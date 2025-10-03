# tests/test_users.py
import pytest
def user_payload(uid=1, name="Paul", email="pl@atu.ie", age=25, sid="S1234567"):
 return {"user_id": uid, "name": name, "email": email, "age": age, "student_id": sid} #builds user dictionary for requests

def test_create_user_ok(client): #creates user and verifies fields
 r = client.post("/api/users", json=user_payload())
 assert r.status_code == 201
 data = r.json()
 assert data["user_id"] == 1
 assert data["name"] == "Paul"

def test_duplicate_user_id_conflict(client): #test functino to check if 2 user witht he same id returns 409 error
 client.post("/api/users", json=user_payload(uid=2)) #creates user with user id 2
 r = client.post("/api/users", json=user_payload(uid=2)) #tries to create user with user id 2 again
 assert r.status_code == 409 # duplicate id -> conflict
 assert "exists" in r.json()["detail"].lower()

@pytest.mark.parametrize("invalid_email", ["plainaddress", "test@", "@domain.com"]) #invalid email should be caught by pydanticc and return 422
def test_bad_email_422(client, invalid_email):
 r = client.post("/api/users", json=user_payload(uid=3, email=invalid_email))
 assert r.status_code == 422 # pydantic validation error

@pytest.mark.parametrize("bad_sid", ["BAD123", "s1234567", "S123", "S12345678"]) #invalid student ids should fail the schema validation and return 422
def test_bad_student_id_422(client, bad_sid):
 r = client.post("/api/users", json=user_payload(uid=3, sid=bad_sid))
 assert r.status_code == 422 # pydantic validation error

def test_update_then_404(client): 
 client.post("/api/users", json=user_payload(uid=3, name="Initialname"))
 r1 = client.put("/api/users/3", json=user_payload(uid=3, name="Updatedname"))#first update should succeed
 assert r1.status_code == 200
 r2 = client.put("/api/users/10", json=user_payload(uid=3, name="Updatedname"))#second update should fail since user 10 doesnt exist
 assert r2.status_code == 404

def test_get_user_404(client):
 r = client.get("/api/users/999") #returning non existent user returns an error
 assert r.status_code == 404

def test_delete_then_404(client):
 client.post("/api/users", json=user_payload(uid=10))
 r1 = client.delete("/api/users/10") #first delete succceeds
 assert r1.status_code == 204
 r2 = client.delete("/api/users/10") # second delete fails since user10 is already deleted
 assert r2.status_code == 404

