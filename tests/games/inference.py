from tests.locals import *



# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w  C     C              1     Cw
# w             C         1      w
# w1111111111    C        1111111w
# w         1   C2C  C        2  w
# w         1  C C         C     w
# w    C         A               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

# """

# up, up, up, up, left
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              1             1 w
# w                            1 w
# w              2               w
# w                    2         w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#combine with avatar sam bounceFoward. works.
#0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w              A               w
# w                         3 3  w
# w         c    c               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# TODO: You need to be able to re-run testAndExpand() when no hypotheses pass your filter
## the problem here is that you need to build on expandSprite proposals with expandLine within one errorMap and
## you don't ordinarily do that.
#0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w              A          3 3  w
# w         c    c               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# works if you don't allow the eventHandler to apply effects to newly-created sprites
#[0,0,0,K_LEFT, K_LEFT,0,0]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w                         3 3  w
# w         c    c A             w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# #up, up, down
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              1               w
# w              1               w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#0,0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              1               w
# w              1               w
# w              A          3 3  w
# w   c   c                      w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                       1      w
# w                       1      w
# w1111111111    C        1111111w
# w         1   C2C           2  w
# w         1    C               w
# w              A               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w                              w
# w                              w
# w            1 C               w
# w                              w
# w                      A       w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """