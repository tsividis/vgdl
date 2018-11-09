install.packages("cowplot")
library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")
# dates=c('nov8_local')
## oct23 actually now contains runs from 10/20,10/21,10/24,10/25: this is:
## IW1 vs IW2, lha 2 vs 10, nF TF, and the beginnings of the absolute_max_nodes=50k
## oct26: IW1 vs IW2, with lha2, mN=50k
## oct31: burn_in lesions, but only partial. lots of models haven't finished running yet; lots haven't even started.
## nov5: e-greedy
## nov8: IW2
dates = c('oct26','nov8')#, 'nov5')
data = list()
for (date in dates){
  path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
  d=read.csv(path, header=TRUE, na.strings='NA')
  
  if ('exploration_burn_ins' %in% names(d)){
    d$exploration_burn_ins = as.numeric(d$exploration_burn_ins) ## you might want to make this as.numeric()
  }else{
    d$exploration_burn_ins = NA
  }
  
  if(length(data)==0){
    data = d
  }
  else{
    for(colname in names(d)){
      if (!(colname %in% names(data))){
        d[,colname] = NA
      }
    }
    for(colname in names(data)){
      if(!(colname %in% names(d))){
        data[,colname]=NA
      }
    }
    data = rbind(data,d)
  }
}
# path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
# data=read.csv(path, header=TRUE, na.strings='NA')
game_names = c(levels(data$game_name))
data$modelrun_ID = as.factor(data$modelrun_ID)
data$timestep = as.numeric(as.character(data$timestep))
data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
data$local_score = as.numeric(as.character(data$score))
data$all_score = as.numeric(as.character(data$cumulative_max_score))
data$agent_type = as.factor(data$agent_type)
data$score = as.numeric(as.character(data$sparse_score))
## TODO: once you're using human data, move this below and run it for all_data
## remove 'variant_' from names
data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))


# plotpath = paste('~/Projects/atari/vgdl/',date,'/plots', sep='')
# dir.create(plotpath)

## load dqn data
dqnpath = 'dqn'
oldformatdqngames = c('aliens','avoidgeorge','plaqueattack','survivezombies')
dqndata = list()

for (game in oldformatdqngames){
  filename=paste(game,'_1win.csv',sep='')
  path = paste('~/Projects/atari/vgdl/dqn/old_format/',filename, sep='')
  d=read.csv(path, header=TRUE, na.strings='NA')
  d$game_name = as.factor(game)
  d$score = as.numeric(d$ep_reward)
  d$agent_type = as.factor("DDQN")
  d$ep_reward = NULL
  d$cumulative_steps = as.numeric(d$steps)
  d$criteria = as.factor(1)
  d$steps = NULL
  d$cumulative_wins = as.numeric(0)
  for (i in 2:length(d$level)){
    if (d$level[i]>d$level[i-1]){
      d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
    }
    else{
      d$cumulative_wins[i] = d$cumulative_wins[i-1]
    }
  }
  if(length(dqndata)==0){
    dqndata = d
  }
  else{
    dqndata = rbind(dqndata,d)
  }
}

path = '~/Projects/atari/vgdl/dqn/new_format/'
list.files(path)
for (gamefile in list.files(path)){
  filename = paste(path,gamefile,sep='')
  d=read.csv(filename, header=TRUE, na.strings='NA')
  d$score = d$ep_reward
  d$ep_reward = NULL
  d$cumulative_steps = d$steps
  d$agent_type = as.factor("DDQN")
  d$steps = NULL
  d$win = NULL
  d$cumulative_wins = as.numeric(0)
  for (i in 2:length(d$level)){
    if (d$level[i]>d$level[i-1]){
      d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
    }
    else{
      d$cumulative_wins[i] = d$cumulative_wins[i-1]
    }
  }
  dqndata = rbind(dqndata,d)
}
  
  
for (colname in names(data)){
  if (!(colname %in% names(dqndata))){
    dqndata[,colname] = NA
    print(colname)
  }
}
for (colname in names(dqndata)){
  if (!(colname %in% names(data))){
    data[,colname] = NA
    print(colname)
  }
}

data = rbind(data, dqndata)

colors = c('steelblue1', 'steelblue2', 'steelblue3', 'steelblue4',
           # 'palegreen3', 'seagreen3','darkolivegreen1',
           'firebrick2', 'tomato2', 'salmon', 
           'purple2', 'mediumorchid2', 
           'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')

# colors = c('firebrick2', 'tomato2', 'salmon', 
#            'steelblue3', 'steelblue1', 
#            'palegreen3', 'seagreen3','darkolivegreen1',  
#            'purple2', 'mediumorchid2', 
#            'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')

names(colors)=levels(data$agent_type)
colorScale = scale_color_manual(name="agent_type", values=colors)

games = c("aliens", "avoidgeorge", "plaqueattack", "expt_push_boulders", "expt_relational", "frogs", "portals", "sokoban")
## make dqn/MEP learning-curve plots:
plots = list()
q=list()
max_num_agents = 0
for (i in 1:length(games)){
  game = games[i]
  d = subset(data, game_name==game)
  
  p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
    colorScale+ 
    # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
    scale_color_manual(values=colors) + theme(legend.position="none")+
    ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5))
  
  p=p+ylim(0,5)+xlim(0,30000)#+theme(legend.position='none')
  
  # p
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
  plots[[i]]=p
  num_agents = length(unique(d$agent_type))
  if (num_agents>max_num_agents){
    max_num_agents = num_agents
    
    p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
    p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
      scale_color_manual(values=colors) + theme(legend.position="right")+
      ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5))
    
    legend = g_legend(p) 
    grid.newpage()
    q[[1]]=ggdraw(legend)
  }
}
layout = matrix(c(1:8), ncol=4, byrow=TRUE)
m = multiplot(plotlist = plots[1:8], layout=layout)


# stand_in_dqn = list()
# for game in levels(data$game_name){
#   if (!(game %in% levels(dqndata$game_name))){
#     d = data.frame(game_name=as.character(), level=as.numeric(), agent_type=as.character(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric())
#    r = data.frame(game_name=game, level=0, agent_type='DDQN', cumulative_steps=)
#     }
# }

## load human data
humandatapaths = c('pilot_Oct29th_Full','pilot_Oct30th_Full')
date='oct28_local'
humandata = list()
for (humandatapath in humandatapaths){
  path = paste('~/Projects/atari/vgdl/',date, '/csv_data/', humandatapath,'.csv', sep='')
  d=read.csv(path, header=TRUE, na.strings='NA')
  if (length(humandata)==0){
    humandata = d
  }
  else{
    humandata = rbind(humandata,d)
  }
}

humandata$agent_type=as.factor('human')
humandata$subject_ID = as.factor(humandata$subject)
humandata$subject = NULL ## drop old name
humandata$modelrun_ID = as.factor('oct29')
humandata$condition = as.factor('full')
humandata$game_name = as.factor(humandata$gameName)
humandata$gameName = NULL
humandata$level_number = humandata$gameLevel
humandata$gameLevel = NULL
humandata$cumulative_wins = humandata$levels_won
humandata$levels_won = NULL
humandata$exploration_burn_ins = as.factor(0)
humandata$timestep = humandata$steps
humandata$steps = NULL
humandata$levelscore=humandata$score
humandata$score=0

humandata$levels_lost = NULL ##idk what this is; we don't need it
humandata$group = NULL ## drop this for now. it refers to the groupings of the games we gave to people
humandata$gameNumber = NULL
humandata$gameRound = NULL

## fix cumulative_timesteps
humandata$cumulative_timestep = 1
for (i in 2:length(humandata$timestep)){
  prevrow = humandata[i-1,]
  row = humandata[i,]
  if (row$subject_ID==prevrow$subject_ID & row$game_name==prevrow$game_name){
    humandata[i,]$cumulative_timestep = prevrow$cumulative_timestep + 1
    if (row$level_number==prevrow$level_number){
      humandata[i,]$score = prevrow$score + (row$levelscore-prevrow$levelscore)
    }
    else if (row$level_number > prevrow$level_number){
      humandata[i,]$score = prevrow$score
    }
  }
}
##remove first part of game string from humandata names
humandata$game_name = as.factor(as.character(lapply(as.vector(humandata$game_name), remove_string_from_name)))
humandata$levelscore = NULL
humandata$level_number = as.factor(humandata$level)
## now make sure that humandata has all the column names that data has.
for (colname in names(data)){
  if (!(colname %in% names(humandata))){
    humandata[,colname] = NA
    print(colname)
  }
}

## and vice-versa
for (colname in names(humandata)){
  if (!(colname %in% names(data))){
    data[,colname] = NA
    print(colname)
  }
}

## make a single dataframe
alldata = rbind(data, humandata)

##example plot for one game
game = levels(humandata$game_name)[6]
p = ggplot(subset(alldata,game_name==game), aes(x=cumulative_timestep,y=cumulative_wins,color=agent_type))
p+geom_point()+geom_smooth()+ggtitle(game)

game=levels(humandata$game_name)[2]
p = ggplot(subset(alldata,game_name==game), aes(x=cumulative_timestep,y=score,color=agent_type))
p+geom_point()+geom_smooth()+ggtitle(game)


## this is weird when you plot by level_number and also when you plot by subject. looks like I took more actions
## even in the games where that's not really possible (like surprise)
p = ggplot(humandata, aes(x=real_time,fill=subject_ID))
p=p+geom_histogram(binwidth=1,aes(y=..density..))+facet_wrap(~game_name)+xlim(0,1000)
p


## plot wins
max_num_agents = 0
plots = list()
q=list()
for (i in 1:length(levels(data$game_name))){
  game = levels(data$game_name)[i]
  d=subset(data, game_name==game & agent_type!="IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lr=False")
  
  p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
    colorScale+ 
    # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
    scale_color_manual(values=colors) + theme(legend.position="none")+
    ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5))
  
  p=p+ylim(0,5)#+theme(legend.position='none')
  
  # p
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
      scale_color_manual(values=colors) + theme(legend.position="right")+
      ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
    
    legend = g_legend(p) 
    grid.newpage()
    q[[1]]=ggdraw(legend)
  }
  newdir=paste('~/Projects/atari/vgdl/',date,'/plots/',sep='')
  dir.create(newdir, showWarnings = FALSE)
  
  newdir=paste('~/Projects/atari/vgdl/',date,'/plots/levels_won/',sep='')
  # newdir=paste('~/Projects/atari/vgdl/',date,'/plots/e_greedy/',sep='')
  dir.create(newdir, showWarnings = FALSE)
  title = paste('~/Projects/atari/vgdl/',date,'/plots/levels_won/', game, '.png', sep='')
  # title = paste('~/Projects/atari/vgdl/',date,'/plots/e_greedy_/', game, '.png', sep='')
  ggsave(title, plot=p, width=15, height=10)
}


## plot scores
plots = list()
for (i in 1:length(levels(data$game_name))){
  game = levels(data$game_name)[i]
  
  p=ggplot(subset(data, (game_name==game) ), aes(x=cumulative_steps, y=level_accumulated_score, color=agent_type)) ##color=agent_type
  p=p+geom_point(size=1, position=position_jitter(width=.1,height=.1))+
    geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
    scale_color_manual(values=colors) + theme(legend.position="right")+
    ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
  # p
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
  if (game%in%c('lemmings', 'lemmings_2','lemmings_3')){
    p=p+ylim(min(na.omit(filter(data, game_name==game)$level_accumulated_score)),50)
  }
  
  plots[[i]] = p
  newdir=paste('~/Projects/atari/vgdl/',date,'/plots/score/',sep='')
  dir.create(newdir, showWarnings = FALSE)
  title = paste('~/Projects/atari/vgdl/',date,'/plots/score/', game, '.png', sep='')
  ggsave(title, plot=p, width=15, height=10)  
}


#####
#####
### playing around with plotting exploration lesion data.
colors = c('firebrick2', 'steelblue1', 'salmon', 
           'steelblue3', 'steelblue1', 
           'palegreen3', 'seagreen3','darkolivegreen1',  
           'purple2', 'mediumorchid2', 
           'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')
data$fburn_ins = as.factor(data$exploration_burn_ins)

for(game in levels(data$game_name)){
  d = subset(data,game_name==game)
  print(game)
  print(unique(d$exploration_burn_ins))
}


game = levels(data$game_name)[1]
d = subset(data,game_name==game)
# names(colors)=levels(data$exploration_burn_ins)
# colorScale = scale_color_manual(name="exploration_burn_ins", values=colors)
p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=as.factor(exploration_burn_ins)))
p=p+geom_point() +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)#+theme(legend.position="none")
p

+
  scale_color_manual(values=colors) + theme(legend.position="none")+
  ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) # try geom_smooth(method='loess')
p


data$exploration_burn_ins = as.factor(data$exploration_burn_ins)

names(colors)=levels(data$exploration_burn_ins)
colorScale = scale_color_manual(name="exploration_burn_ins", values=colors)

## you're plotting based on the interaction but that gives you a discrete color scale, so you'd have to specify it manually. Maybe the thing
## to do is make up a segmentation of some color spectrum (after you've seen the various points of the theory values).
p=ggplot(data, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
p=p+geom_point() +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)
p

#####
#####
## create blank data frame object so we can move the legend to the right.
# df <- data.frame()
# w = ggplot(df) + geom_point() +xlim(0,1) 
w=list()
w[[1]] = ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type)) + geom_blank() + theme_classic() +   theme(line = element_blank(),
                                                                                                                           text = element_blank(),
                                                                                                                           title = element_blank())
layout = matrix(c(1:96), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[1:90],q[1]), layout=layout)

## Making two plots for now because multiplot refuses to make the first 4 plots if
## you make the whole grid at once.
layout = matrix(c(c(1:46),47,48), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[1:46],w[1],q[1]), layout=layout)

layout = matrix(c(c(1:45),46,46,47), ncol=6, byrow=TRUE)
m = multiplot(plotlist = c(plots[47:length(plots)], q[1]), layout=layout)

###
games_to_levels = data.frame(game_name=as.character(), num_levels=as.numeric())
for (i in 1:length(levels(data$game_name))){
  game_name=levels(data$game_name)[i]
  num_levels = 5
  if ( (grepl('expt', game_name)) | (grepl('bees', game_name) )| (grepl('corridor',game_name))| 
       (grepl('closing',game_name)) ){
    num_levels=4
  }
  if ((grepl('expt_ee', game_name)) | (grepl('expt_preconditions_1', game_name)) ){
    num_levels=6
  }
  if (game_name %in% c('expt_preconditions', 'expt_preconditions_2')){
    num_levels=5
  }
  new = data.frame(game_name=game_name, num_levels=num_levels)
  games_to_levels = rbind(games_to_levels, new)
}

## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                          max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                          level_num=as.numeric())
for (j in 1:length(levels(data$agent_type))){
  agent = levels(data$agent_type)[j]
  # if (length(unique(subset(data, agent_type==agent)$game_name))<80){
  #   print(paste('warning; you have fewer than 80 games for agent: ',agent, sep=''))
  # }
  # else{
    for (i in 1:length(levels(data$game_name))){
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
  # }
}
## grouping by games and variants is no longer necessary, because you removed 'variant' from the game_names, 
## so they're naturally alphabetized.
# plantimedata = transform(plantimedata,game_name=factor(game_name, levels=all_game_names))
plantimedata = mutate(plantimedata, level_percentage=max_levels_won/level_num)
plantimedata = mutate(plantimedata, score_efficiency=max_score/max_steps)
plantimedata = mutate(plantimedata, plan_efficiency=score_efficiency/planning_time)
plantimedata = mutate(plantimedata, plan_nodes_per_step=planning_time/max_steps)

## summary plot of overall results -- easy to look at.
p = ggplot(subset(plantimedata, game_name!='boulderchase_1'), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+scale_fill_manual(values=colors)
p
## save as 10x16

## plot idx_1 vs idx_3
for (i in 1:length(levels(data$agent_type))){
  agent = levels(data$agent_type)[i]
  p = ggplot(subset(data, agent_type==agent), aes(x=planner_settings))
  p=p+geom_histogram(breaks=c(0.5,1.5,2.5,3.5,4.5),aes(y=..density..))+facet_wrap(~game_name)
  p
}

## same thing but not grouped by game. not easy to read.
# p = ggplot(plantimedata, aes(x=reorder(game_name,-level_percentage), y=level_percentage, fill=factor(agent_type))) +
#   geom_bar(position='dodge', stat='identity')+
#   theme(axis.text.x = element_text(angle = 90, hjust = 1))+scale_fill_manual(values=colors)
# p
## save as 6x72

## To see roughly what this plot'll look like, fill in a fake score_efficiency column
for (i in 1:length(levels(plantimedata$game_name))){
  game = levels(plantimedata$game_name)[i]
  if(length(filter(plantimedata, agent_type==levels(data$agent_type)[4] & game_name==game))){
    new = data.frame(game_name=game, agent_type='DDQN', max_score=NA, 
                     max_steps=NA, planning_time=NA, 
                     max_levels_won=NA,level_percentage=NA,
                     level_num=5, score_efficiency=0.001)
    plantimedata = rbind(plantimedata, new)    
  }


}

## you're unable to make colors show up on this. why??
p = ggplot(subset(plantimedata, (agent_type%in%c(levels(plantimedata$agent_type)[4],'DDQN')) & !is.na(score_efficiency)), 
           aes(x=reorder(game_name,score_efficiency), y=score_efficiency))+
    geom_bar(position='dodge', stat='identity')+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p+coord_flip()


# p = ggplot(plantimedata, aes(x=game_name, y=score_efficiency, fill=factor(agent_type))) +
#   geom_bar(position='dodge', stat='identity')+
#   theme(axis.text.x = element_text(angle = 90, hjust = 1))
# p


## plot failures across models for each game
p = ggplot(plantimedata, aes(x=game_name, y=1-level_percentage, fill=factor(modelrun_ID))) +
  geom_bar(position='dodge', stat='identity', alpha=.7)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
p

## plot means and sd for each model. Probably the most useful figure you can make as you decide what to do.
## But careful -- figure may be misleading because you're omitting NAs 
## (game/model combinations that you don't yet have data for) 
means = data.frame(model=as.character(), mean=as.numeric(), sd=as.numeric())
for (i in 1:length(levels(plantimedata$agent_type))){
  agent = levels(plantimedata$agent_type)[i]
  if (length(subset(plantimedata, agent_type==agent)$game_name)<80){
    print(paste('warning; you have fewer than 80 games for agent: ',agent, sep=''))
  }
  else{
    num = summarise(subset(plantimedata, agent_type==levels(plantimedata$agent_type)[i]), 
                    percentage_mean=mean(level_percentage), percentage_sd=sd(level_percentage))
    r = data.frame(model=levels(plantimedata$agent_type)[i], percentage_mean=num$percentage_mean, percentage_sd=num$percentage_sd)
    means=rbind(means,r)
  }
}
means = na.omit(means)
p = ggplot(means, aes(x=reorder(model,-percentage_mean) ,y=percentage_mean, color=model))+
  geom_pointrange(aes(ymin=percentage_mean-percentage_sd, ymax=percentage_mean+percentage_sd))+ylim(0,1.2)+
  colorScale+ xlab('agent type') + ylab('% levels won')+  theme(axis.text.x=element_blank(),
                                                                axis.ticks.x=element_blank())
p

##plot of avg plantime per action
plantimeplots = list()
for (i in 1:length(levels(plantimedata$agent_type))){
  agent = levels(plantimedata$agent_type)[i]
  d = subset(plantimedata, agent_type==agent)
  if (length(d$game_name)>0){
    p = ggplot(d, aes(x=reorder(game_name, plan_nodes_per_step),y=plan_nodes_per_step,fill=level_percentage))
    p=p+geom_bar(position='dodge',stat='identity')+ggtitle(as.character(agent)) +theme(axis.text.x = element_text(angle = 90, hjust = 1))
    p=p+scale_fill_gradient2(low="red",high="green",midpoint=.6)
    p
    plantimeplots[[i]]=p
  }
}
layout = matrix(c(1:length(plantimeplots)), ncol=1, byrow=TRUE)
m = multiplot(plotlist = plantimeplots, layout=layout)
## save as 32x16




####
####
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





###
### load helper functions
g_legend <- function(a.gplot){ 
  tmp <- ggplot_gtable(ggplot_build(a.gplot)) 
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box") 
  legend <- tmp$grobs[[leg]] 
  return(legend)} 

remove_string_from_name = function(name){
  strings_to_remove = c('gvgai_variant','expt_variant', 'variant','gvgai')
  for (i in 1:length(strings_to_remove)){
    string_to_remove = strings_to_remove[i]
    if (grepl(string_to_remove, name)){
      keep = substr(name, nchar(string_to_remove)+2, nchar(name))
      return(keep)
    }
    else{
      keep=name
    }
  }
  return(name)
}


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
