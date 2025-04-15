function addNumbers(a, b) {
    return a + b;
}

console.log(addNumbers(5, "10"));

const obj = {
    name: "Alice",
    age: 25
};

Object.freeze(obj);
obj.age = 30; 

function recursive() {
    recursive();
}
setTimeout(recursive, 1000);

const arr = new Array(999999999);
