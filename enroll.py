from db import (
    create_user,
    get_user_by_email,
    deactivate_cards,
    assign_card,
    deactivate_faces,
    save_face,
)

from nfc_reader import read_uid
from face_ai import face_capture


def main():
    print("=== User Enrollment ===")

    email = input("Email: ").strip().lower()
    user = get_user_by_email(email)

    if user:
        user_id = user["user_id"]
        print("User found")
    else:
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        role = input("Role(admin/user): ").strip().lower() or "user"
        user_id = create_user(first_name, last_name, email, role)
        print("User created")

    print("Please tap card")
    uid = read_uid()

    if not uid:
        print("No card UID read")
        raise SystemExit

    deactivate_cards(user_id)
    assign_card(user_id, uid)
    print(f"Card assigned: {uid}")

    print("Look at camera")
    face_bytes = face_capture()

    if not face_bytes:
        print("Unable to recognise")
        raise SystemExit

    deactivate_faces(user_id)
    save_face(user_id, face_bytes, "face_ai_recognition_v1")

    print("Enrollment complete!")


if __name__ == "__main__":
    main()
"""from db import create_user, get_user_email, deactivate_cards, assign_card, deactivate_faces, save_face
#from nfc_reader import read_uid
#from face_ai import face_capture



email = input("Email:").strip() #get users input and take away unnessary parts
user = get_user_email(email) #variable for function in db and email input
if user:
    user_id = user["user_id"] #find the users id in the row of the db function and see if it matches
    print("user found")
else:
    first_name = input("First name:")
    last_name = input("Last name:")
    role = input("Role(admin/user): ") or "user"
    user_id = create_user(first_name, last_name, email, role)
    print("user created")

print("please tap card")
uid = read_uid()


deactivate_cards(user_id)
assign_card(user_id,uid)

print("look at camera and press enter")
input()
face_bytes = face_capture()
if not face_bytes:
    print("unable to recognise")
    raise SystemExit

deactivate_faces(user_id)
save_face(user_id, face_bytes, "face_ai_recognition_v1") #label stored in database vector
print("enrollment complete!")"""





















