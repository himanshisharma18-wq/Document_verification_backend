
# DATABASE TEST


from backend.database.demo_database import (
    PASSPORT_DATABASE,
    find_passport
)


print()
print("========================================")
print("DEMO PASSPORT DATABASE")
print("========================================")

print()
print("TOTAL RECORDS:")
print(len(PASSPORT_DATABASE))


print()
print("SEARCHING FOR TEST PASSPORT...")
print("----------------------------------------")

passport = find_passport(
    "G2762794<"
)


if passport:

    print("PASSPORT FOUND: True")

    print()
    print("PASSPORT RECORD:")
    print(passport)

else:

    print("PASSPORT FOUND: False")


print()
print("========================================")
print("DATABASE TEST COMPLETE")
print("========================================")