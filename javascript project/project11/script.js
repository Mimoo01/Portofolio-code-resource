function test(a, b) {
  console.log("a awal", a);

  console.log("b awal", b);

  [a, b] = [b, a];

  // final
  console.log("a final", a);
  console.log("b final", b);
}

// function untuk membuat palindrom test

function palindrom_test(test) {
  let str = test;
  if (typeof test === "number") {
    str = test.toString();
  }

  let reversed = str.split("").reverse().join("");

  if (str === reversed) {
    console.log("merupakan bilangan palindrom");
  } else {
    console.log("bukan merupakan bilangan palindrom");
  }
}

// test(10, 20);
palindrom_test(121);

// soal no 3

var twoSum = function (nums, target) {
  let sum = 0;
  for (let i = 0; i < nums.length; i++) {
    let start = i + 1;
    for (let n = start; n < nums.length; n++) {
      sum = nums[i] + nums[n];
      if (sum === target) {
        console.log("[", i, ",", n, "]");
      }
    }
  }
};

// soal  no 4

class Node {
  constructor(val) {
    this.val = val;
    this.next = null;
  }
}

var addTwoNumbers = function (l1, l2) {
  let result1 = "";
  let result2 = "";
  while (l1) {
    result1 = l1.val + result1; // ini kuncinya
    l1 = l1.next;
  }
  while (l2) {
    result2 = l2.val + result2;
    l2 = l2.next;
  }

  let sum = Number(result1) + Number(result2);
  console.log("Hasilnya adalah", sum);
  let str = sum.toString();
  let arr = str.split("").reverse(); // ["3","0","8"];

  let head = new Node(Number(arr[0]));
  let current = head;

  for (let i = 1; i < arr.length; i++) {
    current.next = new Node(Number(arr[i]));
    current = current.next;
  }

  return head;
};
