# Dungeon Blitz - Preservation Files

This repository holds data of Dungeon Blitz Flash game.
Before everything, for testing purposes, change `DungeonBlitz.swf` file with the one on the releases. So you can redirect server to correct ports to connect with settled on [`config.js`](src\config.js) file.

## Play the Game

-   [Download Flash Point](https://flashpointarchive.org/downloads) to run game.
    -   Launch command[^1]: http://db.bmgstatic.com/p/cbv/DungeonBlitz.swf?fv=cbq&gv=cbv

### Run Server

You can use `npm run start` or `node main.js`. You can also use:

```sh
node .
```

### Optional

-   [Download JPEXS](https://github.com/jindrapetrik/jpexs-decompiler/releases) to see `swf` files.[^2]

[^1]: You have to set this on Flash's launch command.
[^2]: You will need Java to run JPEXS. Even on MacOS.
