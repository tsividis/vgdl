install.packages("cowplot")
library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")

date = c('oct22')
path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
data=read.csv(path, header=TRUE, na.strings='NA')
game_names = c(levels(data$game_name))
#data = na.omit(data)
data$modelrun_ID = as.factor(data$modelrun_ID)
data$timestep = as.numeric(as.character(data$timestep))
data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
data$local_score = as.numeric(as.character(data$score))
data$all_score = as.numeric(as.character(data$cumulative_max_score))
data$agent_type = as.factor(data$agent_type)
data$score = as.numeric(as.character(data$sparse_score))

plotpath = paste('~/Projects/atari/vgdl/',date,'/plots', sep='')
dir.create(plotpath)


g_legend <- function(a.gplot){ 
  tmp <- ggplot_gtable(ggplot_build(a.gplot)) 
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box") 
  legend <- tmp$grobs[[leg]] 
  return(legend)} 


## TODO: normalize score by max_score for that game.
## TODO: bind specific colors to specific models so that it looks the way you want.
## TODO: find a good layout for all the games. for now, pretend you have data for more games than you do so you can make the plots??

## you'll need to specify the game order manually anyway, because otherwise the layout will break the games up.
## one page with 4s, 3s, and 2s
## one page with 5s
##
all_game_names = c('aliens', 'variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
               'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
               'bait', 'variant_bait_1', 'variant_bait_2',
               'bees_and_birds','variant_bees_and_birds_1',  
               'boulderchase', 'variant_boulderchase_1',
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
               'surprise', 'variant_surprise_1', 'variant_surprise_2',
               'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
               'watergame', 'variant_watergame_1', 'variant_watergame_2',
               'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3')

existing_games = list()
missing_games = list()
j=1
k=1
for (i in 1:length(all_game_names)){
  if (all_game_names[i] %in% game_names){
    existing_games[j] = all_game_names[i] 
    j = j+1
  }
  else{
    missing_games[k] = all_game_names[i]
    k = k+1
  }
}


## color mapping:
agent_types = c('human', 'params__IW=1__ea=False','params__IW=1__ea=True', 
                'params__IW=2__ea=False',  'params__IW=2__ea=True', 'DDQN')
# colors = c('blue','lightskyblue3', 'lightskyblue1', 
           # 'steelblue2', 'steelblue4', 'salmon3')
##you need to make a real mapping between agent_types and colors. for now, just have
## as many colors as you have agent_types in the plot:
colors = c('steelblue3','steelblue1')
## Make plots.

## plot scores
plots = list()
for (i in 1:length(existing_games)){
  game = existing_games[i]

    p=ggplot(subset(data, (game_name==game)&(agent_type=='params__IW=2__ea=True') ), aes(x=cumulative_steps, y=level_accumulated_score, color=modelrun_ID)) ##color=agent_type
    p=p+geom_point(size=1, position=position_jitter(width=.1,height=.1),color='steelblue3')+
      geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5, color='steelblue3')+
      #  scale_color_manual(values=colors) + #theme(legend.position="none")+
      #
      ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
    p
  p=p+ylim(0,max(na.omit(filter(data, game_name==game)$level_accumulated_score)))
  if (grepl('frogs', game)){
    p=p+ylim(0,60)
  }
  if ( (grepl('bees', game) )| (grepl('corridor',game))| (grepl('closing',game)) | (grepl('surprise',game))){
    p=p+ylim(0,40)
  }
    if (grepl('expt', game)){
      if (grepl('expt_ee',game)){
        p=p+ylim(0,60)
      }
      else{
        p=p+ylim(0,40)
      }
    }
  if (game%in%c('lemmings','variant_lemmings_2','variant_lemmings_3')){
    p=p+ylim(min(na.omit(filter(data, game_name==game)$level_accumulated_score)),50)
  }

  plots[[i]] = p
  #title = paste('~/Projects/atari/vgdl/',date,'/plots/modelcomp_', game, '.png', sep='')
  #ggsave(title, plot=p, width=15, height=10)
}

colors = c('firebrick2', 'steelblue3', 'green3', 'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')

names(colors)=levels(data$agent_type)
colorScale = scale_color_manual(name="agent_type", values=colors)

max_num_agents = 0
## plot wins
plots = list()
q=list()
for (i in 1:length(existing_games)){
    game = existing_games[i]
    d=subset(data, game_name==game)
    if (game=='variant_frogs_2'){
      d = subset(d, grepl('22',d$modelrun_ID))
    }
    if (game=='variant_expt_relational_2'){
      d = subset(d, grepl('21', d$modelrun_ID))
    }

    p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
    p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
      #colorScale+ 
            # scale_color_manual(values=colors)+
        # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
      scale_color_manual(values=colors) + theme(legend.position="none")+
      ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
    
    p=p+ylim(0,5)#+theme(legend.position='none')

    p
    if ((grepl('expt', game)) | (grepl('surprise',game)) | (grepl('bees', game))| (grepl('corridor',game))| (grepl('closing',game))){
      if (grepl('expt_ee',game)){
        p=p+ylim(0,6)
      }
      else if (grepl('surprise', game)){
        p=p+ylim(0,5)
      }
      else{
        p=p+ylim(0,4)
      }
    }

  plots[[i]] = p
  num_agents = length(unique(d$agent_type))
  if (num_agents>max_num_agents){
    max_num_agents = num_agents
    
    p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
    p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
      #colorScale+ 
      # scale_color_manual(values=colors)+
      # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
      scale_color_manual(values=colors) + #theme(legend.position="none")+
      ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
    
    legend = g_legend(p) 
    grid.newpage()
    q[[1]]=ggdraw(legend)
    #q[[1]] = grid.draw(legend)
  }
  #title = paste('~/Projects/atari/vgdl/',date,'/plots/levels_won_', game, '.png', sep='')
  #ggsave(title, plot=p, width=15, height=10)
}

## create blank data frame object so we can move the legend to the right.
df <- data.frame()
w = ggplot(df) + geom_point() +xlim(0,1) + theme_classic()


layout = matrix(c(1:96), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[1:91],q[[1]]), layout=layout)

## Making two plots for now because multiplot refuses to make the first 4 plots if
## you make the whole grid at once.
layout = matrix(c(1:48), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[1:46],q[[1]]), layout=layout)

layout = matrix(c(1:48), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[47:length(plots)],q[[1]]), layout=layout)

###
###
###(old version)
games_to_levels = data.frame(game_name=as.character(), num_levels=as.numeric())
for (i in 1:length(levels(data$game_name))){
    game_name=levels(data$game_name)[i]
    num_levels = 5
    if ( (grepl('expt', game_name)) | (grepl('bees', game_name) )| (grepl('corridor',game_name))| 
        (grepl('closing',game_name)) ){
      num_levels=4
    }
    if ((grepl('expt_ee', game_name)) | (grepl('variant_expt_preconditions_1', game_name)) ){
      num_levels=6
    }
    new = data.frame(game_name=game_name, num_levels=num_levels)
    games_to_levels = rbind(games_to_levels, new)
}
## Make vertical plot of score/time per game/planner.
# plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
#                           max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric())
# for (i in 1:length(levels(data$game_name))){
#   for (j in 1:length(levels(data$agent_type))){
#     s = subset(data, ((game_name==levels(data$game_name)[i]) & (agent_type==levels(data$agent_type)[j])) )
#     ## the row we want
#     r = filter(s, cumulative_timestep==max(cumulative_timestep))[1,]
#     ## take only the relevant columns and put them in the new data frame
#     new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
#                      max_steps=r$cumulative_timestep, planning_time=r$cumulative_planner_nodes, 
#                     max_levels_won=max(r$cumulative_wins))
#     plantimedata = rbind(plantimedata, new)
#   }
# }
# plantimedata = na.omit(plantimedata)
# plantimedata = mutate(plantimedata, score_efficiency=max_score/max_steps)
# plantimedata = mutate(plantimedata, plan_efficiency=score_efficiency/planning_time)


## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                          max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                          level_num=as.numeric())
for (i in 1:length(levels(data$game_name))){
  for (j in 1:length(levels(data$agent_type))){
    s = subset(data, ((game_name==levels(data$game_name)[i]) & (agent_type==levels(data$agent_type)[j])) )
    if (length(s$level_max_score)>0){
      ## the row we want
      r = filter(s, cumulative_timestep==max(cumulative_timestep))[1,]
      ## take only the relevant columns and put them in the new data frame
      new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                     max_steps=r$cumulative_timestep, planning_time=r$cumulative_planner_nodes, 
                     max_levels_won=max(r$cumulative_wins),
                     level_num=filter(games_to_levels, (game_name==r$game_name))$num_levels)
      plantimedata = rbind(plantimedata, new)
    }
    }
}
plantimedata = na.omit(plantimedata)
plantimedata = mutate(plantimedata, level_percentage=max_levels_won/level_num)
plantimedata = mutate(plantimedata, score_efficiency=max_score/max_steps)
plantimedata = mutate(plantimedata, plan_efficiency=score_efficiency/planning_time)

## plot failures across models for each game
p = ggplot(plantimedata, aes(x=game_name, y=1-level_percentage, fill=factor(modelrun_ID))) +
  geom_bar(position='dodge', stat='identity', alpha=.7)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p

## plot means and sd for each model. Probably the most useful figure you can make as you decide what to do.
means = data.frame(model=as.character(), mean=as.numeric(), sd=as.numeric())
for (i in 1:length(levels(plantimedata$agent_type))){
  num = summarise(subset(plantimedata, agent_type==levels(plantimedata$agent_type)[i]), 
                  percentage_mean=mean(level_percentage), percentage_sd=sd(level_percentage))
  r = data.frame(model=levels(plantimedata$agent_type)[i], percentage_mean=num$percentage_mean, percentage_sd=num$percentage_sd)
  means=rbind(means,r)
}
means = na.omit(means)
p = ggplot(means, aes(x=reorder(model,-percentage_mean) ,y=percentage_mean, color=model))+
  geom_pointrange(aes(ymin=percentage_mean-percentage_sd, ymax=percentage_mean+percentage_sd))+ylim(0,1.2)+
  colorScale+ xlab('agent type') + ylab('% levels won')+  theme(axis.text.x=element_blank(),
                   axis.ticks.x=element_blank())
p


model_run1 = '2018-10-15_'
model_run2 = '2018-10-18_'
plot_overlap = function(plantimedata, model_run1, model_run2){
  plots = list()
    p = ggplot(subset(plantimedata, modelrun_ID%in%c(model_run1, model_run2)) , aes(x=reorder(game_name,-level_percentage), y=level_percentage, fill=factor(modelrun_ID))) +
  geom_bar(position='identity',stat='identity', alpha=.5)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p
}

######
######


diffdata = data.frame(game_name=as.character(), agent_type=as.character(), model_run = as.character(), max_score=as.numeric(), 
                          max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric())
for (i in 1:length(levels(data$game_name))){
  for (j in 1:length(levels(data$modelrun_ID))){
    s = subset(data, ((game_name==levels(data$game_name)[i]) & (modelrun_ID==levels(data$modelrun_ID)[j])) )
    ## the row we want
    r = filter(s, cumulative_timestep==max(cumulative_timestep))[1,]
    ## take only the relevant columns and put them in the new data frame
    new = data.frame(game_name=r$game_name, agent_type=r$agent_type, model_run=r$modelrun_ID, max_score=r$score, 
                     max_steps=r$cumulative_timestep, planning_time=r$cumulative_planner_nodes, max_levels_won=max(r$cumulative_wins))
    diffdata = rbind(diffdata, new)
  }
}

get_diff = function(diffdata, model_run1, model_run2){
  ## makes a histogram of improvements in model_run1 over model_run2
  
  diff_frame = data.frame(game_name=as.character(), level_diff=as.numeric(), col=as.character())
  
  colors = c('red','green2')
  for (i in 1:length(levels(diffdata$game_name))){
    game = levels(diffdata$game_name)[i]
    m1=subset(diffdata, game_name==game&model_run==model_run1)$max_levels_won
    m2=subset(diffdata, game_name==game&model_run==model_run2)$max_levels_won        
    d = m1-m2
    if (length(d)==0){
      d = NA
      col=NA
    }else{
    if (d<0){
        col=1
      }else{
        col=2
      }
    }
    new = data.frame(game_name=game, level_diff=d, col=col)
    diff_frame = rbind(diff_frame, new)
  }
  diff_frame$col = as.factor(diff_frame$col)
  p = ggplot(diff_frame, aes(x=reorder(game_name,-level_diff), y=level_diff, color=col))+
    geom_bar(position='dodge', stat='identity')+scale_color_manual(values=colors)+scale_fill_manual(values=colors)+
    theme(axis.text.x = element_text(angle = 90, hjust = 1))
  p
  
}



p = ggplot(plantimedata, aes(x=reorder(game_name,-max_levels_won), y=max_levels_won, fill=factor(modelrun_ID))) +
  geom_bar(position='dodge', stat='identity')+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p

p = ggplot(plantimedata, aes(x=game_name, y=score_efficiency, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p


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
