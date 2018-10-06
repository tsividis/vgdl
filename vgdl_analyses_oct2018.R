library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")

date = c('oct6')
path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
data=read.csv(path, header=TRUE)
game_names = c(levels(data$game_name))

data$timestep = as.numeric(as.character(data$timestep))
data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
data$local_score = as.numeric(as.character(data$score))
data$score = as.numeric(as.character(data$cumulative_max_score))

plotpath = paste('~/Projects/atari/vgdl/',date,'/plots', sep='')
dir.create(plotpath)

## TODO: normalize score by max_score for that game.
## TODO: bind specific colors to specific models so that it looks the way you want.
## TODO: find a good layout for all the games. for now, pretend you have data for more games than you do so you can make the plots??

## you'll need to specify the game order manually anyway, because otherwise the layout will break the games up.
## one page with 4s, 3s, and 2s
## one page with 5s
##
all_game_names = c('avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
               'aliens', 'variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
               'bait', 'variant_bait_1', 'variant_bait_2',
               'bees_and_birds','variant_bees_and_birds_1',  
               'boulderdash', 'variant_boulderdash_1',
               'butterflies', 'variant_butterflies_1', 'variant_butterflies_2',
               'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3',
               'closing_gates', 'variant_closing_gates_1',
               'corridor','variant_corridor_1', 
               'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2',
               'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
               'expt_helper', 'variant_expt_helper_1', 'variant_expt_helper_2',
               'expt_preconditions', 'variant_expt_preconditions_1', 'variant_expt_preconditions_2',
               'expt_push_boulders', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2',
               'expt_relational', 'variant_expt_relational_1', 'variant_expt_relational_2',
               'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
               'jaws', 'variant_jaws_1', 'variant_jaws_2',
               'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
               'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
               'myAliens', 'variant_myAliens_1', 'variant_myAliens_2',
               'portals', 'variant_portals_1', 'variant_portals_2',
               'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
               'sokoban', 'variant_sokoban_1', 'variant_sokoban_2',
               'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
               'watergame', 'variant_watergame_1', 'variant_watergame_2',
               'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3')
existing_games = list()

## Make plots.
plots = list()
# for (i in 1:length(game_names)){
for (i in 1:24){
  game = game_names[i]
  p=ggplot(subset(data, game_name==game), aes(x=cumulative_steps, y=score, color='agent_type')) ##color=agent_type
  p=p + geom_point(color='steelblue3') + geom_smooth(span=.5, se=FALSE, color='steelblue3') + 
    expand_limits(y=0) +
    ggtitle(game) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
  p 
  plots[[i]] = p
  #title = paste('~/Projects/atari/vgdl/',date,'/plots/modelcomp_', game, '.png', sep='')
  #ggsave(title, plot=p, width=15, height=10)
}

layout = matrix(c(1:24), nrow=4, byrow=TRUE)
## takes a really long time to run, for some reason.
#m = multiplot(plotlist = plots, cols=6)
m = multiplot(plotlist = plots, layout=layout)

title = paste('~/Projects/atari/vgdl/',date,'/plots/multiplot1.png',sep='')
ggsave(m, file=title, dpi=600)


# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}
