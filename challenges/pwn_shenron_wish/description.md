# ⭐ Shenron Ultimate Wish

> *"I am the Eternal Dragon. State your wish."*

The seven Dragon Balls have been gathered. Shenron has been summoned.

But the wish-granting service has a **critical vulnerability**. Exploit it to bypass the authentication check and force Shenron to grant YOUR wish — the flag.

## Connection

```
nc pwn.dbzctf.local 1337
```

## Files

Download the challenge binary: [shenron](files/shenron)

## Background

The service reads your wish into a fixed-size buffer. Something about the way it handles input feels... unsafe.

Overflow the buffer, seize control of the instruction pointer, and redirect execution to `grant_wish()`.

```c
void grant_wish(char *team_token) {
    // Only true Saiyans reach here
    printf("Your flag: THA{%s}\n", team_token);
}

void make_wish() {
    char wish[64];
    printf("State your wish: ");
    gets(wish);   // <-- ??
}
```

**This challenge uses dynamic per-team flags.** Your flag is unique to your team.

---

*First Blood earns the 🩸 First Blood badge and eternal glory.*
