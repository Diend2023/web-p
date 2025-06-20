export function header() {
    const menuBtn = document.querySelector(".menu-btn")
    const navigation = document.querySelector(".navigation")

    menuBtn.addEventListener("click", () => {
        menuBtn.classList.toggle("active");
        navigation.classList.toggle("active");

        const navigation_items = document.querySelector(".navigation-items");
        
        for (let i = 0; i < navigation_items.children.length; i++) {
            navigation_items.children[i].addEventListener("click", () => {
                menuBtn.classList.remove("active");
                navigation.classList.remove("active");
            });
        }
    });

    // navigation.addEventListener("click", () => {
    //     menuBtn.classList.remove("active");
    //     navigation.classList.remove("active");
    // });
};