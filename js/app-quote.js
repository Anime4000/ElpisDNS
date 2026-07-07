const footerQuotes = [

    "“If you use technology, this fight is yours.” — EFF",

    "“Privacy is not something that I’m merely entitled to, it’s an absolute prerequisite.” — Marlon Brando",

    "“Arguing that you don't care about privacy because you have nothing to hide is like saying you don't care about free speech because you have nothing to say.” — Edward Snowden",

    "“The internet interprets censorship as damage and routes around it.” — John Gilmore",

    "“A network built upon strong foundations shall not falter.”",

    "“Defend privacy. Preserve freedom. Protect the open internet.”",

    "“Blessed are the peacemakers of the network.”",

    "“A heavenly guardian against corrupted routes and digital darkness.”",

    "“Truth travels faster upon open networks.”",

    "“The gates shall remain open to all who seek knowledge.”",

    "“Privacy is sacred. Freedom is foundational.”"
];

const randomQuote =
    footerQuotes[
        Math.floor(Math.random() * footerQuotes.length)
    ];

document.getElementById("footer-quote")
    .innerText = randomQuote;