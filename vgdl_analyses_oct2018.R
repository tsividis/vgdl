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
## Make plots.
for (i in 1:length(game_names)){
  game = game_names[i]
  p=ggplot(subset(data, game_name==game), aes(x=cumulative_steps, y=score, color='agent_type')) ##color=agent_type
  p=p + geom_point(color='steelblue3') + geom_smooth(span=.5, se=FALSE, color='steelblue3') # try geom_smooth(method='loess')
  p 
  title = paste('~/Projects/atari/vgdl/',date,'/plots/modelcomp_', game, '.png', sep='')
  ggsave(title, plot=p, width=15, height=10)
}



