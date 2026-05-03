const faqData = [
  {
    question: "What is JavaScript?",
    answer: "JavaScript is a programming language commonly used in web development to create interactive effects within web browsers.",
  },
  {
    question: "What is an FAQ Accordion?",
    answer: "An FAQ Accordion is a user interface component that allows users to expand and collapse sections of content, typically used for frequently asked questions.",
  },
  {
    question: "How do I create an FAQ Accordion?",
    answer:
      "You can create an FAQ Accordion using HTML, CSS, and JavaScript. The HTML structure typically consists of a list of questions and answers, while CSS is used for styling, and JavaScript is used to handle the expand/collapse functionality.",
  },
];

// // get accordion container element
const accordionContainer = document.getElementById("accordion");

function generateAccordionItems(faqData) {
  faqData.forEach((item) => {
    const accordionItem = document.createElement("div");
    accordionItem.classList.add("accordion-item");
    const header = document.createElement("button");
    header.classList.add("accordion-header");
    header.textContent = item.question;
    const content = document.createElement("div");
    content.classList.add("accordion-content");
    const contentText = document.createElement("p");
    contentText.textContent = item.answer;

    // insert element to HTML
    content.appendChild(contentText);
    accordionItem.appendChild(header);
    accordionItem.appendChild(content);

    // add accordion item to accordion container
    accordionContainer.appendChild(accordionItem);
  });
}
// // call function generate faq
generateAccordionItems(faqData);

const accordionHeaders = document.querySelectorAll(".accordion-header");

// // add event listener for accordion
accordionHeaders.forEach((header) => {
  header.addEventListener("click", () => {
    header.classList.toggle("active");
    const content = header.nextElementSibling;

    if (header.classList.contains("active")) {
      content.style.maxHeight = content.scrollHeight + "px";
    } else {
      content.style.maxHeight = 0;
    }

    accordionHeaders.forEach((otherHeader) => {
      if (otherHeader !== header && otherHeader.classList.contains("active")) {
        otherHeader.classList.remove("active");

        const otherContent = otherHeader.nextElementSibling;
        otherContent.classList.remove("active");
        otherContent.style.maxHeight = 0;
      }
    });
  });
});

// document.addEventListener("DOMContentLoaded", () => {
//   const faqData = [
//     {
//       question: "What is JavaScript?",
//       answer: "JavaScript is a programming language commonly used in web development to create interactive effects within web browsers.",
//     },
//     {
//       question: "What is an FAQ Accordion?",
//       answer: "An FAQ Accordion is a user interface component that allows users to expand and collapse sections of content.",
//     },
//     {
//       question: "How do I create an FAQ Accordion?",
//       answer: "You can create an FAQ Accordion using HTML, CSS, and JavaScript.",
//     },
//   ];

//   const accordionContainer = document.getElementById("accordion");

//   // generate accordion
//   faqData.forEach((item) => {
//     const accordionItem = document.createElement("div");
//     accordionItem.classList.add("accordion-item");

//     const header = document.createElement("button");
//     header.classList.add("accordion-header");
//     header.textContent = item.question;

//     const content = document.createElement("div");
//     content.classList.add("accordion-content");

//     const contentText = document.createElement("p");
//     contentText.textContent = item.answer;

//     content.appendChild(contentText);
//     accordionItem.appendChild(header);
//     accordionItem.appendChild(content);
//     accordionContainer.appendChild(accordionItem);

//     // 🔥 event langsung dipasang di sini (lebih aman)
//     header.addEventListener("click", () => {
//       const isActive = header.classList.contains("active");

//       // tutup semua
//       document.querySelectorAll(".accordion-header").forEach((h) => {
//         h.classList.remove("active");
//       });

//       document.querySelectorAll(".accordion-content").forEach((c) => {
//         c.style.maxHeight = null;
//       });

//       // buka yang diklik (kalau sebelumnya tertutup)
//       if (!isActive) {
//         header.classList.add("active");
//         content.style.maxHeight = content.scrollHeight + "px";
//       }
//     });
//   });
// });
