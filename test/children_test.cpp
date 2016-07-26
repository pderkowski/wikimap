#include "catch.hpp"
#include "children.hpp"
#include <cstdlib>

TEST_CASE("Can iterate const children", "[children]") {
    const Children children;

    int count = 0;
    for (auto c : children) {
        ++count;
    }

    REQUIRE(count == 4);
}

TEST_CASE("Can iterate non-const children", "[children]") {
    Children children;

    int count = 0;
    for (auto& c : children) {
        c = nullptr;
        ++count;
    }

    REQUIRE(count == 4);
}

TEST_CASE("Can set-get children", "[children]") {
    Children children;

    char* nodeptr = (char*)malloc(4*sizeof(char));

    children.setTopLeft((Node*)nodeptr);
    children.setTopRight((Node*)(nodeptr + 1));
    children.setBottomRight((Node*)(nodeptr + 2));
    children.setBottomLeft((Node*)(nodeptr + 3));

    SECTION("Const case") {
        const char* tl = reinterpret_cast<const char*>(children.getTopLeft());
        const char* tr = reinterpret_cast<const char*>(children.getTopRight());
        const char* br = reinterpret_cast<const char*>(children.getBottomRight());
        const char* bl = reinterpret_cast<const char*>(children.getBottomLeft());

        REQUIRE(tl - nodeptr == 0);
        REQUIRE(tr - nodeptr == 1);
        REQUIRE(br - nodeptr == 2);
        REQUIRE(bl - nodeptr == 3);
    }

    SECTION("Non-const case") {
        char* tl = reinterpret_cast<char*>(children.getTopLeft());
        char* tr = reinterpret_cast<char*>(children.getTopRight());
        char* br = reinterpret_cast<char*>(children.getBottomRight());
        char* bl = reinterpret_cast<char*>(children.getBottomLeft());

        REQUIRE(tl - nodeptr == 0);
        REQUIRE(tr - nodeptr == 1);
        REQUIRE(br - nodeptr == 2);
        REQUIRE(bl - nodeptr == 3);
    }
}