library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")
library(purrr)
library(zoo)
library(EnvStats)
library(grid)


## the fact that you're unable to change dataframes within functions
## is forcing you to keep saving/resaving variables with different names
## and it's forcing you to keep copy/pasting scripts all over the place.
## start by figuring out the function thing, and then you can clean the
## rest up more easily.

original_games = c('aliens', 'antagonist', 'avoidgeorge', 'bait', 'bees_and_birds', 'boulderdash', 'butterflies',
                   'chase', 'closing_gates', 'corridor', 'ee', 'frogs', 'helper', 'jaws', 
                   'lemmings', 'missilecommand', 'myAliens', 'plaqueattack', 'portals', 'preconditions','push_boulders',
                   'relational','sokoban', 'surprise', 'survivezombies', 'watergame','zelda')

## oct23 actually now contains runs from 10/20,10/21,10/24,10/25: this is:
## IW1 vs IW2, lha 2 vs 10, nF TF, and the beginnings of the absolute_max_nodes=50k
## oct26: IW1 vs IW2, with lha2, mN=50k
## oct31: burn_in lesions, but only partial. lots of models haven't finished running yet; lots haven't even started.
## nov5: e-greedy
## nov8: IW2
## nov12: 5x IW1, ix IW2, missing frogs.
## nov 15,16: frogs.
## nov 18, nov 19: informal sensitivity analysis
## nov27: exploration and planner lesions
## nov28: AGH+IW planner lesion
dates = c('nov8', 'nov12', 'nov15', 'nov16', 'dec4')
## warning: don't plot frogs from anything before nov13b
dates = list('jan27')
saveddata = data
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
data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))

#### Crap for fast analysis. delete soon.
for (colname in names(MEPdata3)){
  if (!(colname %in% names(data))){
    data[,colname] = NA
    print(colname)
  }
}
for (colname in names(data)){
  if (!(colname %in% names(MEPdata3))){
    MEPdata3[,colname] = NA
    print(colname)
  }
}

lesion_games = levels(data$game_name)
data = rbind(data, subset(MEPdata3, game_name%in%lesion_games))

for (colname in names(humandata)){
  if (!(colname %in% names(data))){
    data[,colname] = NA
    print(colname)
  }
}
for (colname in names(data)){
  if (!(colname %in% names(humandata))){
    humandata[,colname] = NA
    print(colname)
  }
}
data = rbind(data, subset(humandata, game_name%in%lesion_games))

p=ggplot(subset(data, game_name%in%lesion_games), aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
p=p+geom_point()+geom_jitter()+geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+theme(legend.position="none")+facet_wrap(~game_name)
p

p=ggplot(subset(data, game_name=='sokoban'), aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
p=p+geom_point()+geom_jitter() +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+theme(legend.position="none")
p


## you want to get the human_normed composite ratio and then make the raster plot for all the models.


#### new crap for fast analysis ends here.

for (colname in names(dqndata)){
  if (!(colname %in% names(data))){
    data[,colname] = NA
    print(colname)
  }
}


exploration_lesions = subset(data, grepl('eG=True', agent_type))
planner_lesions = subset(data, grepl('PL=', agent_type))

new_planner_lesions = subset(data, grepl('PL=', agent_type))
planner_lesions = rbind(planner_lesions, new_planner_lesions)


MEPdatawoSubjectID=MEPdata
MEPdata = data

# d$cumulative_wins = as.numeric(0)
# for (i in 2:length(d$level)){
#   if (d$level[i]>d$level[i-1]){
#     d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
#   }
#   else{
#     d$cumulative_wins[i] = d$cumulative_wins[i-1]
#   }
# }
# if(length(dqndata)==0){
#   dqndata = d
# }
# else{
#   dqndata = rbind(dqndata,d)
# }
# # }

saveddqndata = dqndata
dqndata = list()
path = '~/Projects/atari/vgdl/dqn/'
oldformatdqngames = c('aliens','avoidgeorge','plaqueattack','survivezombies')

list.files(path)
for (gamefile in list.files(path)){
  filename = paste(path,gamefile,sep='')
  gamenamestart = unlist(gregexpr('dqn/',filename))+nchar('dqn/')
  gamenameend = unlist(gregexpr('_reward', filename))-1
  game = substr(filename, gamenamestart, gamenameend)
  d=read.csv(filename, header=TRUE, na.strings='NA')
  
  d$score = d$ep_reward
  d$game_name = as.factor(remove_string_from_name(game))
  d$ep_reward = NULL
  d$criteria = as.factor(1)
  d$cumulative_steps = d$steps
  d$agent_type = as.factor("DDQN")
  d$subject_ID = as.factor("DDQN")
  d$steps = NULL
  d$win = NULL
  d$cumulative_wins = as.numeric(0)
  d$sparse_levels_won = NA
  row = data.frame(level=0,score=0,game_name=game,criteria=as.factor(1),cumulative_steps=0,agent_type='DDQN',subject_ID='DDQN',cumulative_wins=0, sparse_levels_won=0)
  
  for (i in 2:length(d$level)){
    if (d$level[i]>d$level[i-1]){
      d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
      d$sparse_levels_won[i] = d$cumulative_wins[i]
    }
    else{
      d$cumulative_wins[i] = d$cumulative_wins[i-1]
    }
  }
  dqndata = rbind(dqndata,d)
}

# dqndata$game_name = as.factor(as.character(lapply(as.vector(dqndata$game_name), remove_string_from_name)))

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
alldata = rbind(alldata, dqndata)

# colors = c('orange','steelblue1','steelblue3')
# names(colors) = levels(MEPdata2$agent_type)
# colorScale = scale_color_manual(name='agent_type',values=colors)

colors = c('purple2', #'mediumorchid2', 
           'steelblue1',# 'steelblue2',# 'steelblue3', 'steelblue4',
           # 'palegreen3', 'seagreen3','darkolivegreen1',
           'firebrick2', 'tomato2', 'salmon', 
           'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')

names(colors)=levels(data$agent_type)
inversecolors = levels(data$agent_type)
names(inversecolors) = colors[1:length(levels(data$agent_type))]
colorScale = scale_color_manual(name="agent_type", values=colors)

# games = c("aliens", "avoidgeorge", "plaqueattack", "expt_push_boulders", "expt_relational", "frogs", "portals", "sokoban")
## make dqn/MEP learning-curve plots:
plots = list()
q=list()
max_num_agents = 0
for (i in 1:length(levels(dqndata$game_name))){
  game = levels(dqndata$game_name)[i]
  d = subset(data, game_name==game)
  
  p=ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5)+
    colorScale+ 
    # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
    scale_color_manual(values=colors) + theme(legend.position="none")+
    ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5))
  
  p=p+ylim(0,5)#+xlim(0,30000)#+theme(legend.position='none')
  
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
layout = matrix(c(1:26), ncol=4, byrow=TRUE)
m = multiplot(plotlist = plots[1:8], layout=layout)

p = ggplot(filter(data, game%in%levels(dqndata$game_name)), aes(x=cumulative_steps,y=cumulative_wins, color=agent_type))
p=p+geom_point()+geom_smooth()+facet_wrap(~game_name)+theme(legend.position="none")
p


# stand_in_dqn = list()
# for game in levels(data$game_name){
#   if (!(game %in% levels(dqndata$game_name))){
#     d = data.frame(game_name=as.character(), level=as.numeric(), agent_type=as.character(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric())
#    r = data.frame(game_name=game, level=0, agent_type='DDQN', cumulative_steps=)
#     }
# }

## load human data

# date='humandata_new'
# humandatapaths = list.files("~/Projects/atari/vgdl/humandata_new/csv_data")

date='humandata'
humandatapaths = list.files("~/Projects/atari/vgdl/humandata")

humandata = list()
for (humandatapath in humandatapaths){
  path = paste('~/Projects/atari/vgdl/',date, '/', humandatapath, sep='')
  d=read.csv(path, header=TRUE, na.strings='NA')
  if (length(humandata)==0){
    humandata = d
  }
  else{
    humandata = rbind(humandata,d)
  }
}

oldhumandata=humandata

humandata$agent_type=as.factor('human')

humandata$modelrun_ID = as.factor('oct29')
humandata$condition = as.factor('full')

humandata$game_name = as.factor(humandata$game_name)

# humandata$subject_ID = as.factor(humandata$subject)
# humandata$subject = NULL ## drop old name column
# humandata$game_name = as.factor(humandata$gameName)
# humandata$gameName = NULL
# humandata$level_number = humandata$gameLevel
# humandata$gameLevel = NULL
# humandata$cumulative_wins = humandata$levels_won
# humandata$levels_won = NULL

humandata$exploration_burn_ins = as.factor(0)
humandata$levels_lost = NULL ##idk what this is; we don't need it
humandata$group = NULL ## drop this for now. it refers to the groupings of the games we gave to people
humandata$gameNumber = NULL
humandata$gameRound = NULL

p = ggplot(subset(humandata, game_name=='ee_3' & subject_ID=='Sy4k9pvpm'), aes(x=cumulative_steps, y=sparse_levels_won, color=subject_ID))+geom_point()+geom_smooth(method='loess', span=1,se=FALSE)
p = ggplot(subset(humandata, game_name=='push_boulders_2'), aes(x=cumulative_steps, y=sparse_levels_won, color=subject_ID))+geom_point()+geom_smooth(method='loess', span=1,se=FALSE)
p = ggplot(subset(humandata, game_name=='plaqueattack_1'), aes(x=cumulative_steps, y=sparse_levels_won, fill='steelblue3'))+geom_point()+geom_smooth(method='loess',se=FALSE)

p

## for new-format humandata:
# humandata$cumulative_steps = humandata$timestep
## fix cumulative_timesteps
### I don't think you need to run this.
# humandata$cumulative_timestep = 1
# for (i in 2:length(humandata$timestep)){
#   prevrow = humandata[i-1,]
#   row = humandata[i,]
#   if (row$subject_ID==prevrow$subject_ID & row$game_name==prevrow$game_name){
#     humandata[i,]$cumulative_timestep = prevrow$cumulative_timestep + 1
#     if (row$level_number==prevrow$level_number){
#       humandata[i,]$score = prevrow$score + (row$levelscore-prevrow$levelscore)
#     }
#     else if (row$level_number > prevrow$level_number){
#       humandata[i,]$score = prevrow$score
#     }
#   }
# }

s = subset(humandata, game_name==game)
for (i in 1:length(unique(s$subject_ID))){
  ID = unique(s$subject_ID)[i]
  print(c(ID, length(filter(s, s$subject_ID==ID)$sparse_levels_won)))

  }

##remove first part of game string from humandata names. no longer needed because csv files have the right names.
# humandata$game_name = as.factor(as.character(lapply(as.vector(humandata$game_name), remove_string_from_name)))

humandata$levelscore = NULL
# humandata$cumulative_steps = humandata$cumulative_timestep
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


savedalldata = alldata
alldata = rbind(alldata, data)
## make a single dataframe
alldata = rbind(data, humandata)
colors = c('purple2', #'mediumorchid2', 
           'steelblue1',# 'steelblue2',# 'steelblue3', 'steelblue4',
           'palegreen3',# 'tomato2', 'salmon', 
           'firebrick2',# 'seagreen3','darkolivegreen1',
           'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')

names(colors)=levels(alldata$agent_type)
inversecolors = levels(alldata$agent_type)
names(inversecolors) = colors[1:length(levels(alldata$agent_type))]
colorScale = scale_color_manual(name="agent_type", values=colors)

### alldata has to be (humandata, dqndata, MEPdata)
humancolors = rep('palegreen3', length(unique(humandata$subject_ID)))
# MEPcolors = c('steelblue3', 'steelblue1')
IW1subjs = unique(subset(MEPdata, agent_type==levels(MEPdata$agent_type)[2])$subject_ID)
IW2subjs = unique(subset(MEPdata, agent_type==levels(MEPdata$agent_type)[1])$subject_ID)
IW1subj_length = length(IW1subjs)
IW2subj_length = length(IW2subjs)
MEPcolors = c(rep('steelblue1', IW1subj_length), rep('steelblue1', IW2subj_length)) ####this is broken -- will show both EMPA models in the same color.
dqncolors = 'grey50'
colors = c(humancolors, dqncolors, MEPcolors)
# names(colors) = c(unique(humandata$subject_ID), 'DDQN', IW1subjs)
# names(colors) = c(unique(humandata$subject_ID), 'DDQN', IW1subjs, IW2subjs)
# colors = c(humancolors, dqncolors, IW1colors)
names(colors)=unique(alldata$subject_ID)
colorScale = scale_color_manual(name="subject_ID", values=colors)

## change this once you have more agents?

for (i in 1:length(levels(humandata$game_name))){
  game = levels(humandata$game_name)[i]
  p = ggplot(filter(humandata,game_name==game), aes(x=cumulative_frames,y=cumulative_wins,color=subject_ID))
  p=p+geom_point()+geom_smooth()+ggtitle(game)+theme(legend.position="none")#+colorScale+scale_color_manual(values=colors)+theme(legend.position="none")
  plots[[i]] = p
}



### MAIN LEARNING-CURVE PLOTS"""
# games_to_show = c('aliens_2', 'missilecommand', 'butterflies_1', 'plaqueattack_1', 'portals')
## Find best DDQN games:
## assuming you've made plantimedata already:
df = subset(plantimedata, agent_type=='DDQN'&game_name%in%original_games)
games_to_show = df[order(-df$level_percentage, -df$composite_ratio),][1:16,]$game_name


#games_to_show = c(as.character(games_to_show), as.character(df[order(df$level_percentage, df$composite_ratio),][1:4,]$game_name))

games_to_show = c('myAliens', 'survivezombies','helper','avoidgeorge', 'missilecommand', 'antagonist', 'preconditions', 'closing_gates',
                 'aliens','frogs', 'zelda', 'sokoban', 'butterflies', 'chase', 'bait', 'push_boulders')
games_to_show = c('myAliens', 'avoidgeorge','survivezombies', 'antagonist', 'frogs','butterflies', 'zelda', 'bait')
games_to_show = c('avoidgeorge','missilecommand','antagonist','butterflies','zelda','bait')

sorted_game_names = sort(as.vector(unique(alldata$game_name)))
## plotting all agents/models
plots = list()
for (i in 1:length(sorted_game_names)){
# for (i in 1:length(levels(alldata$game_name))){
# for(i in 1:length(games_to_show)){
  # game = levels(alldata$game_name)[i]
  # geom_smooth(method='loess',se=FALSE)
  # game = games_to_show[i]
  game = sorted_game_names[i]
  # if (game %in% c('myAliens', 'avoidgeorge', 'survivezombies')){
  #   max_x=3000
  # }
  # else{
  #   max_x = 1000
  # }
  max_x = 10000
  d = subset(alldata, game_name==game&agent_type %in% c('human', 'DDQN', levels(alldata$agent_type)[4]))
  # d$level_accumulated_score = d$score
  p = ggplot(d, aes(x=cumulative_steps,y=cumulative_wins,color=subject_ID, size=agent_type))
  p=p+geom_point()+ 
    ggtitle(game)+theme(legend.position="none")+scale_size_manual(values=c(1,1,1))+scale_color_manual(values=colors)+colorScale+
  # p=p+scale_color_manual(values=colors,name="Model",
                                       # breaks=c("DDQN", levels(alldata$agent_type)[4],
                                       # labels=c("DDQN", "EMPA")+
    xlab('Steps taken by agent')+ylab('Levels won')
    # p=p+xlim(0,1000000)
  # p=p+xlim(0,100000)
  # if(length(subset(d, agent_type=='DDQN'&cumulative_steps<(max_x+1))$cumulative_wins)<3){
  if ((length(subset(d, agent_type=='DDQN'&cumulative_steps<(max_x+1))$cumulative_wins)==0) || 
     (max(subset(d, agent_type=='DDQN'&cumulative_steps<(max_x+1))$cumulative_wins)==0)){
      p=p+geom_smooth(data=subset(d,agent_type %in% c('human', levels(alldata$agent_type)[4])),method=loess,span=1,se=FALSE)+
      geom_segment(aes(x=0,y=0,xend=max_x,yend=0),data=subset(d,agent_type=='DDQN'),size=.7)
  }
  else{
    p=p+geom_smooth(method=loess, span=1,se=FALSE)
  }
  p=p+xlim(0,max_x)#+ylim(0,5)
  
  p
  
  plots[[i]] = p
}
layout = matrix(c(1:length(plots)), ncol=4, byrow=TRUE) ##16x20 for 16 games ##10x20 for 12 games
# layout = matrix(c(1:5), ncol=5, byrow=TRUE)
layout = matrix(c(1:90), ncol=6, byrow=TRUE)
layout = matrix(c(1:length(plots)), ncol=3, byrow=TRUE) ##9x12 for 6 games
##6x8 for one game
m = multiplot(plotlist = plots, layout=layout)
multiplot_10k = m
multiplot_1_mil = m
## save as 50x30?

y = c(0,0,0,0,0,0,1,1,2)
x = c(0,1,3,6,8,10,12,20,25)
df = data.frame(x=x,y=y)
p=ggplot(df, aes(x=x,y=y))+geom_point()+  geom_smooth(method='loess',se = FALSE)
p



###return here
s$weight=0.1
# s[which(s$sparse_levels_won==0),]$weight=10
s[which(s$cumulative_wins==max(s$cumulative_wins)),]$weight=1

s=subset(d, agent_type!='human'&subject_ID=='5006QS5')
s=subset(d, agent_type!='human'&subject_ID=='3F6GE42')

p = ggplot(s, aes(x=cumulative_steps,y=sparse_levels_won,color=subject_ID, size=agent_type, weight=weight))
p=p+geom_point()+ geom_smooth(method=loess,span=1,se=FALSE)+#geom_spline(w=c(1,1,1,5))+#geom_smooth(method='lm',span=5,se=FALSE)+
  ggtitle(game)+scale_size_manual(values=c(.6,.6,0.6,.6))+theme(legend.position="bottom")
p+xlim(0,3000)

1
50
122
2198
###

new_e = data.frame(agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric())
points_to_add=200
###add a few data points at the end of each agent's run, IF the agent has won all games.
for (i in 1:length(unique(e$subject_ID))){
  for (j in 1:length(unique(e$game_name))){
    subject = unique(e$subject_ID)[i]
    game = unique(e$game_name)[j]
    s = select(subset(e, subject_ID==subject& game_name==game), agent_type, subject_ID, game_name, cumulative_steps, cumulative_wins)
    if (max(s$cumulative_wins)==5){
      max_steps = max(s$cumulative_steps)
      for (k in 1:points_to_add){
        row = data.frame(agent_type=unique(s$agent_type), subject_ID=subject, game_name=game, cumulative_steps=max_steps+k, cumulative_wins=5)
        s = rbind(s, row)
      }
    }
    new_e = rbind(new_e, s)
  }
}

alldata = rbind(humandata, dqndata, MEPdata)
## another problem: intermediate points are missing for DQN and that breaks smoothing function. mostly a problem for games where dying is hard

## good for zoomed-in plots
p = ggplot(filter(alldata,game_name==game), aes(x=cumulative_steps,y=cumulative_wins,color=subject_ID, size=agent_type))
p=p+geom_point()+geom_smooth(se=FALSE)+ggtitle(game)+theme(legend.position="none")+colorScale+scale_color_manual(values=colors)+scale_size_manual(values=c(1,1,0.6,1))
p=p+xlim(0,10000)
p

## good for non-zoomed-in plots
p = ggplot(filter(alldata,game_name==game), aes(x=cumulative_steps,y=cumulative_wins,color=subject_ID, size=agent_type))
p=p+geom_point()+geom_smooth(se=FALSE)+ggtitle(game)+theme(legend.position="none")+colorScale+scale_color_manual(values=colors)+scale_size_manual(values=c(1,1,1.5,1))
p=p+xlim(0,1000000)
p

d = filter(alldata, game_name=='avoidgeorge')
p = ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
p=p+geom_point()+ggtitle(game)+stat_smooth()+theme(legend.position='none')
p

## build data frame that corresponds to the game we care about
p = ggplot(d, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
p=p+geom_point()+ggtitle(game)+stat_smooth()+theme(legend.position='none')+colorScale+scale_color_manual(values=colors)
p


get_middle_element = function(lst){
  return(lst[round(0.1+length(lst)/2.0)])
}
define_timescale = function(agent, game, quantiles){
  ## agent, e.g., 'DDQN'
  ## quantiles have to be specified as c(.25,.5,...). Also returns x value of max(y)
  d = filter(alldata, agent_type==agent & game_name==game)
  if(length(d$cumulative_wins)==0){
    print(paste("Can't determine quantiles. You don't have data for agent: ", agent, ", game: ", game, sep=''))
  }
  ## find y values (cumulative_wins) that are in the quantiles you asked for
  # quantile_ys = c(round(quantile(d$cumulative_wins, quantiles, names=FALSE)), max(d$cumulative_wins))
  quantile_ys = round(quantile(d$cumulative_wins, quantiles, names=FALSE))
  
  ## find indices that correspond to these
  quantile_indices = map(quantile_ys, function(x) get_middle_element(which(grepl(x,d$cumulative_wins)))[1])
  quantile_xs = map(quantile_indices, function(x) d$cumulative_steps[x])
  if(any(is.na(quantile_xs))){
    print(paste('WARNING -- you have at least one NA in quantile values in define_timescale for game: ',game,', agent: ',agent,', quantiles: ',quantiles, sep=''))
  }
  return(unlist(quantile_xs))
}

get_corresponding_val = function(agent, game, xval, df){
  ## if the interpolation for (agent,game) exists, return the yval that corresponds to the nearest xval
  ## if it doesn't (because the agent's curve finishes well before the requested xval), return the max yval
  
  ## grab rows of the interpolation data frame that corresponds to the agent we want
  relevantrows = filter(df,colour==colors[agent])
  if (xval < max(relevantrows$x)){
    idx = which.min(abs(relevantrows$x-xval))
    # return(max(0.0000000001,relevantrows$y[idx]))
    return(max(0,relevantrows$y[idx]))
    
  }
  else{
    # return(max(0.0000000001,max(relevantrows$y)))
    return(max(0,max(relevantrows$y)))
  }
}

get_corresponding_vals = function(agent, game, xvals, df){
  return(unlist(map(xvals, function(x) get_corresponding_val(agent, game, x, df))))
}

##reference_agent: the agent whose timescale we care about
quantiles = c(.9)
# agent1 = 'human'
agent1 = levels(alldata$agent_type)[2]
agent2 = 'DDQN'

agent_timescale_geom_ratio = function(game, reference_agent, agent1, agent2, agent1_name, agent2_name){
  filtered=filter(alldata,game_name==game & agent_type%in%c(agent1, agent2))
  p = ggplot(filtered, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point()+ggtitle(game)+stat_smooth()+theme(legend.position='none')+colorScale+scale_color_manual(values=colors)
  
  df = ggplot_build(p)$data[[2]]
  
  ##MEP timescale
  reference_agent = agent1
  timescales = define_timescale(reference_agent, game, quantiles) ##also includes xval of max(y)
  vals1 = as.vector(get_corresponding_vals(agent1, game, timescales, df))
  vals2 = as.vector(get_corresponding_vals(agent2, game, timescales, df))
  gm_agent1_scale = geoMean(vals1/vals2)
  
  ##dqn timescale
  reference_agent = agent2
  timescales = define_timescale(reference_agent, game, quantiles) ##also includes xval of max(y)
  vals1 = as.vector(get_corresponding_vals(agent1, game, timescales, df))
  vals2 = as.vector(get_corresponding_vals(agent2, game, timescales, df))
  gm_agent2_scale = geoMean(vals1/vals2)
  
  txt1 = paste(agent1_name, " scale  = ", sprintf("%.2f",gm_agent1_scale), sep='')
  grob1 = grobTree(textGrob(txt1, x=0.1,  y=0.95, hjust=0,
                            gp=gpar(col="black", fontsize=13)))
  
  txt2 = paste(agent2_name, " scale = ", sprintf("%.2f",gm_agent2_scale), sep='')
  grob2 = grobTree(textGrob(txt2, x=0.1,  y=0.90, hjust=0,
                            gp=gpar(col="black", fontsize=13)))
  
  
  ## now calculate the other scale
  all_agent_max = max(df$y)
  
  relevantrows = filter(df,colour==colors[agent1])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent1_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  agent1_pt1 = agent_max/all_agent_max
  agent1_pt2 = agent_max/steps_to_agent_max
  
  relevantrows = filter(df,colour==colors[agent2])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent2_pt1 = agent_max/all_agent_max
  agent2_pt2 = agent_max/steps_to_agent_max
  
  agent2_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  
  score_ratio = agent1_pt1/agent2_pt1
  slope_ratio = agent1_pt2/agent2_pt2
  
  composite_ratio = score_ratio*slope_ratio
  
  row = data.frame(game_name=as.character(game), agent=as.character(agent_type), 
                   score_ratio=as.numeric(score_ratio), slope_ratio=as.numeric(slope_ratio),
                   composite_ratio=as.numeric(composite_ratio), log_composite_ratio=as.numeric(log(composite_ratio)))
  efficiency_dataframe = rbind(efficiency_dataframe,row)
  txt3 = paste("score_ratio = ", sprintf("%.2f",score_ratio), ". slope_ratio = ", sprintf("%.2f",slope_ratio), ". composite ratio = ", sprintf("%.2f",composite_ratio), sep='')
  grob3 = grobTree(textGrob(txt3, x=0.1,  y=0.85, hjust=0,
                            gp=gpar(col="black", fontsize=13)))
  
  p = p+annotation_custom(grob1)+annotation_custom(grob2)+annotation_custom(grob3)
  return(p) ## the mean of the ratios of the values at the supplied quantiles.
}

build_efficiency_dataframe = function(game, reference_agent, agent1, agent2, agent1_name, agent2_name, efficiency_dataframe){
  filtered=filter(alldata,game_name==game & agent_type%in%c(agent1, agent2))
  p = ggplot(filtered, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point()+ggtitle(game)+stat_smooth()+theme(legend.position='none')+colorScale+scale_color_manual(values=colors)
  
  df = ggplot_build(p)$data[[2]]
  
  ##MEP timescale
  reference_agent = agent1
  timescales = define_timescale(reference_agent, game, quantiles) ##also includes xval of max(y)
  vals1 = as.vector(get_corresponding_vals(agent1, game, timescales, df))
  vals2 = as.vector(get_corresponding_vals(agent2, game, timescales, df))
  gm_agent1_scale = geoMean(vals1/vals2)
  
  ##dqn timescale
  reference_agent = agent2
  timescales = define_timescale(reference_agent, game, quantiles) ##also includes xval of max(y)
  vals1 = as.vector(get_corresponding_vals(agent1, game, timescales, df))
  vals2 = as.vector(get_corresponding_vals(agent2, game, timescales, df))
  gm_agent2_scale = geoMean(vals1/vals2)
  
  ## now calculate the other scale
  all_agent_max = max(df$y)
  
  relevantrows = filter(df,colour==colors[agent1])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent1_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  agent1_pt1 = agent_max/all_agent_max
  agent1_pt2 = agent_max/steps_to_agent_max
  
  relevantrows = filter(df,colour==colors[agent2])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent2_pt1 = agent_max/all_agent_max
  agent2_pt2 = agent_max/steps_to_agent_max
  
  agent2_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  
  score_ratio = agent1_pt1/agent2_pt1
  slope_ratio = agent1_pt2/agent2_pt2
  
  composite_ratio = score_ratio*slope_ratio
  
  row = data.frame(game_name=as.character(game), agent=as.character(agent1), 
                   score_ratio=as.numeric(score_ratio), slope_ratio=as.numeric(slope_ratio),
                   composite_ratio=as.numeric(composite_ratio), log_composite_ratio=as.numeric(log(composite_ratio)))
  efficiency_dataframe = rbind(efficiency_dataframe,row)
  
  return(efficiency_dataframe) 
}


## function that returns a dataframe row for the particular game, agent1, agent2 combination. agent2 should just be renamed reference_agent 
## and will eventually be humans, but for now make it MEP as you have the most data for that.
## outer loop can append these rows to a larger dataframe and then you can use that to get the histogram you want.
get_log_ratio = function(game, agent1, agent2){
  filtered=filter(alldata,game_name==game & agent_type%in%c(agent1, agent2))
  p = ggplot(filtered, aes(x=cumulative_steps, y=cumulative_wins,color=agent_type))
  p=p+geom_point()+ggtitle(game)+stat_smooth()+theme(legend.position='none')+colorScale+scale_color_manual(values=colors)
  
  df = ggplot_build(p)$data[[2]]
  
  all_agent_max = max(df$y)
  
  relevantrows = filter(df,colour==colors[agent1])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent1_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  agent1_pt1 = agent_max/all_agent_max
  agent1_pt2 = agent_max/steps_to_agent_max
  
  relevantrows = filter(df,colour==colors[agent2])
  agent_max = max(relevantrows$y)
  steps_to_agent_max = relevantrows$x[which(grepl(agent_max,relevantrows$y))[1]]
  agent2_pt1 = agent_max/all_agent_max
  agent2_pt2 = agent_max/steps_to_agent_max
  
  agent2_composite = (agent_max/all_agent_max)*(agent_max/steps_to_agent_max)
  
  score_ratio = agent1_pt1/agent2_pt1
  slope_ratio = agent1_pt2/agent2_pt2
  
  composite_ratio = score_ratio*slope_ratio
  log_composite_ratio = log(composite_ratio)
  return(c(agent1, game, log_composite_ratio))
}


log_odds_dataframe = data.frame(agent=as.character(), game_name=as.character(), log_ratio=as.numeric())
agent1='DDQN'
for (i in 1:length(levels(dqndata$game_name))){
  game = levels(dqndata$game_name)[i]
  res = get_log_ratio(game, agent1, agent2)
  if (res[3]==-Inf){
    res[3] = -100
  }
  row = data.frame(agent=res[1], game_name=res[2], log_ratio=res[3])
  log_odds_dataframe = rbind(log_odds_dataframe, row)
  ## continue here.
}
d1 = log_odds_dataframe
agent1='human'
for (i in 1:length(levels(humandata$game_name))){
  game = levels(humandata$game_name)[i]
  res = get_log_ratio(game, agent1, agent2)
  if (res[3]==-Inf){
    res[3] = -100
  }
  row = data.frame(agent=res[1], game_name=res[2], log_ratio=res[3])
  log_odds_dataframe = rbind(log_odds_dataframe, row)
}
log_odds_dataframe = subset(log_odds_dataframe, game_name!='sokoban') ## put this back once you have sokoban data.


df = subset(log_odds_dataframe,game_name%in%c('aliens','antagonist','surprise_1'))
df = rbind(df, data.frame(agent=as.character('human'), game_name=as.character('samplegame'), log_ratio="100"))

log_odds_dataframe$log_ratio = as.double(as.character((log_odds_dataframe$log_ratio)))

p = ggplot(log_odds_dataframe, aes(x=reorder(game_name,log_ratio), y=log_ratio, fill=agent))+
  geom_bar(stat='identity',position='dodge')+theme(legend.position="none")+
  # ylim(-10,10)+
  geom_hline(yintercept=0, linetype='dotted')+
  colorScale+
  scale_fill_manual(values=colors) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+xlab('game name')
p+coord_flip()





### MEP vs DQN
agent1 = 'DDQN'
agent2 = levels(alldata$agent_type)[2]
plots = list()
efficiency_dataframe = data.frame(game_name=as.character(), agent=as.character(), 
                                  score_ratio=as.numeric(), slope_ratio=as.numeric(),
                                  composite_ratio=as.numeric(), log_composite_ratio=as.numeric())

for (i in 1:length(levels(dqndata$game_name))){
  game = levels(dqndata$game_name)[i]
  efficiency_dataframe = build_efficiency_dataframe(game, agent2, agent1, agent2,'DDQN', 'MEP', efficiency_dataframe)
}
agent1 = 'human'
for (i in 1:length(levels(humandata$game_name))){
  game = levels(humandata$game_name)[i]
  efficiency_dataframe = build_efficiency_dataframe(game, agent2, agent1, agent2,'human', 'DDQN', efficiency_dataframe)
}
agent1 = 'MEP_wo_position_score'
for (i in 1:length(levels(data$game_name))){
  game = levels(data$game_name)[i]
  efficiency_dataframe = build_efficiency_dataframe(game, agent2, agent1, agent2, agent1, 'MEP', efficiency_dataframe)
}

efficiency_dataframe = subset(efficiency_dataframe, game_name!='sokoban') ## TODO: remove this once you have sokoban.

normalized_by_MEP = efficiency_dataframe


p = ggplot(normalized_by_MEP, aes(x=reorder(game_name,composite_ratio-1), y=composite_ratio-1, fill=agent))+
  geom_bar(stat='identity',position='dodge')+#theme(legend.position="none")+
  # ylim(-10,10)+
  colorScale+
  scale_fill_manual(values=colors) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+xlab('game name')+ggtitle('Composite perf. relative to IW2 w/ default params')
p+coord_flip()




layout = matrix(c(1:28), ncol=4, byrow=TRUE)
m = multiplot(plotlist = plots, layout=layout)

### human vs MEP
agent1 = 'human'
agent2 = levels(alldata$agent_type)[2]
plots = list()
for (i in 1:length(levels(humandata$game_name))){
  game = levels(humandata$game_name)[i]
  p = agent_timescale_geom_ratio(game, agent1, agent1, agent2, 'human', 'MEP')
  plots[[i]] = p
}

layout = matrix(c(1:20), ncol=4, byrow=TRUE)
m = multiplot(plotlist = plots, layout=layout)



## the problem with the geometric mean idea is that we have no good instances to show where the DDQN does better in the way that alphago zero did.
## as in, our model is strictly better.
## but it's still a good idea.

## you need to figure out how to get values for where geom_smooth() hasn't interpolated.


AUC = data.frame(game_name=as.character(), agent_type=as.character(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric())

##TODO: you want to be able to specify some timescale, and then get the AUC up to that timescale.
df = ggplot_build(p)$data[[2]]
relevantrows = filter(df,colour=='palegreen3')
x = relevantrows$x
y = relevantrows$y
id = order(x)
AUC <- sum(diff(x[id])*rollmean(y[id],2))

cutoff = max(x)
modelrows = filter(df, colour=='firebrick2')
x = modelrows$x
modelcutoff = which.min(abs(x-cutoff)) ## point that is closest to the agent x cutoff
x = x[1:modelcutoff]
y = modelrows$y[1:modelcutoff]
id = order(x)
AUC <- sum(diff(x[id])*rollmean(y[id],2))

## first try the easy version: on the human timescale, compare AUCs.

## then to the other, where you extend the human version to calculate the larger AUC.

## assume first element is 0??

## calculate mean subject
## then get AUC

x = 0:10
y = 1*x
df = data.frame(x=x,y=y)
p = ggplot(df, aes(x=x,y=y))
p+geom_point()
id = order(x)
AUC <- sum(diff(x[id])*rollmean(y[id],2))


## this is weird when you plot by level_number and also when you plot by subject. looks like I took more actions
## even in the games where that's not really possible (like surprise)
p = ggplot(humandata, aes(x=real_time,fill=subject_ID))
p=p+geom_histogram(binwidth=1,aes(y=..density..))+facet_wrap(~game_name)+xlim(0,1000)
p

dat = alldata

# 
# for (i in 1:length(unique(d$subject_ID))){
#   f = filter(d, d$subject_ID==unique(d$subject_ID)[i])
#   sum(f$sparse_levels_won)
# }

colors=c('palegreen3', 'orange')
names(colors) = levels(data$agent_type)
colorScale = scale_color_manual(name='agent_type',values=colors)
alldata2=rbind(humandata,data)
alldata3=rbind(humandata, MEPdata)
## plot wins
max_num_agents = 0
plots = list()
q=list()
for (i in 1:length(levels(alldata$game_name))){
  game = levels(alldata$game_name)[i]
  d=subset(alldata, game_name==game & agent_type!='DDQN')
  
  p=ggplot(d, aes(x=cumulative_steps, y=sparse_levels_won,color=subject_ID))
  p=p+geom_point()+ geom_smooth(span=1,se=FALSE)+ #geom_point(size=1,position=position_jitter(width=.05,height=.05), alpha=.5) + #geom_smooth(span=1, se=FALSE, size=1, alpha=0.5)+
    # colorScale+ 
    # p=p+geom_point(size=1,color='steelblue3') +geom_smooth(span=.5, se=FALSE, size=1, alpha=0.5,color='steelblue3')+
    # scale_color_manual(values=colors) + theme(legend.position="none")+
    ggtitle(as.character(game)) + theme(plot.title = element_text(hjust = 0.5)) +theme(legend.position='bottom')
  
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

normaldataframe = dataframe
###
dataframe = rbind(humandata, dqndata, data)

dataframe = rbind(humandata, dqndata, MEPdata, MEPdata2, exploration_lesions, planner_lesions)

games_to_levels = data.frame(game_name=as.character(), num_levels=as.numeric())
for (i in 1:length(levels(dataframe$game_name))){
  game_name=levels(dataframe$game_name)[i]
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

savedplantimedata = plantimedata
## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                          max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                          level_num=as.numeric(), level_efficiency=as.numeric())

for (j in 1:length(levels(dataframe$agent_type))){
  agent = levels(dataframe$agent_type)[j]
  print(agent)
  for (i in 1:length(levels(dataframe$game_name))){
    g = subset(dataframe, game_name==levels(dataframe$game_name)[i])
    print(levels(dataframe$game_name)[i])
    s = subset(g, agent_type==agent)
    if (length(s$level_max_score)>0){
      ## grab each subject's max_steps and max_wins.
        level_maxes = list()
        cumulative_step_maxes = list()
        idx=1
        for (k in 1:length(unique(s$subject_ID))){
          subject = unique(s$subject_ID)[k]
          subjectdata = s[which(s$subject_ID==subject),]
          if (length(subjectdata$cumulative_steps)>0){
            if(max(subjectdata$cumulative_steps)>0){
              level_maxes[[idx]] = max(subjectdata$cumulative_wins)
              cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
              idx = idx+1            
            }

          }
        }
      
      ## calculate the metric you want here. You can normalize it later.
        
      ## mean vector of win numbers
      mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
      ##mean of vector steps-to-win ratios
      l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
      
      
      ## the row we want
      r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
      ## take only the relevant columns and put them in the new data frame
      new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                       max_steps=r$cumulative_steps, planning_time=r$cumulative_planner_nodes, 
                       mean_levels_won=mean_wins,
                       level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                       level_efficiency=l_e)
      plantimedata = rbind(plantimedata, new)
    }
  }
}
## grouping by games and variants is no longer necessary, because you removed 'variant' from the game_names, 
## so they're naturally alphabetized.
# plantimedata = transform(plantimedata,game_name=factor(game_name, levels=all_game_names))
plantimedata = mutate(plantimedata, level_percentage=mean_levels_won/level_num)
plantimedata = mutate(plantimedata, composite_ratio = level_percentage*level_efficiency)
plantimedata = mutate(plantimedata, plan_nodes_per_step=planning_time/max_steps)

  # plantimedata = mutate(plantimedata, level_efficiency=level_percentage/max_steps)
# plantimedata = mutate(plantimedata, composite_ratio=(max_levels_won/all_agent_max_levels)*level_efficiency)
# plantimedata = mutate(plantimedata, plan_efficiency=score_efficiency/planning_time)
plantimedata$human_normed_composite_ratio=NA
plantimedata$EMPA_normed_composite_ratio=NA
##norm by human level_efficiency
for (i in 1:length(levels(plantimedata$game_name))){
  game = levels(plantimedata$game_name)[i]
  human_composite_ratio = subset(plantimedata, agent_type=='human' & game_name==game)$composite_ratio
  EMPA_composite_ratio = subset(plantimedata, agent_type=="IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False"  & game_name==game)$composite_ratio
    for (agent in levels(plantimedata$agent_type)){
    row = plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]
    plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$EMPA_normed_composite_ratio = row$composite_ratio/EMPA_composite_ratio
    
      }
}

for (i in 1:length(plantimedata$human_normed_composite_ratio)){
  if (plantimedata$human_normed_composite_ratio[i]==0){
    plantimedata$human_normed_composite_ratio[i]=0.000000001
  }
  if (plantimedata$EMPA_normed_composite_ratio[i]==0){
    plantimedata$EMPA_normed_composite_ratio[i]=0.000000001
  }
}

representation_lesion_names = c('No Chaser', 'No Missile', 'Missing Speeds', 'No Push', 'No Clone', 'No Destroy', 'No Pull', 'No Teleport', 'No Transform', 'EMPA')

p=ggplot(subset(plantimedata, !(agent_type%in%c('human', levels(plantimedata$agent_type)[10], levels(plantimedata$agent_type)[12]))), aes(agent_type, game_name, fill=log(EMPA_normed_composite_ratio)))+geom_tile()+
# +  theme(axis.text=element_blank(),axis.ticks= element_blank(),axis.title = element_blank(),panel.background = element_blank())
 theme(axis.text.x = element_text(angle = 90, hjust = 1),axis.title = element_blank())+scale_fill_gradient2(low='red', midpoint=0, mid='white', high='green')+
  scale_x_discrete(labels=representation_lesion_names)
p



# plantimedata2 = make_plantimedata(MEPdata2)

# plantimedata = make_plantimedata(alldata)

## summary plot of overall results -- easy to look at.
p = ggplot(subset(plantimedata), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+colorScale+scale_fill_manual(values=colors)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')#+scale_fill_manual(values=colors)
p
## save as 10x16

p = ggplot(subset(plantimedata), aes(x=agent_type, y=log(human_normed_composite_ratio), fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='summary', fun.y='mean')+#facet_wrap(~game_name)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')#+scale_fill_manual(values=colors)
p

plantimesummary = summarySE(plantimedata, measurevar="human_normed_composite_ratio", groupvars=c("agent_type"), na.rm=TRUE)

#### MAIN FIGURE ###
colors = c('palegreen3', 'grey50', 'steelblue1','steelblue3')
names(colors)=levels(alldata$agent_type)
colorScale = scale_color_manual(name="agent_type", values=colors)
main_plot_agent_types = c('DDQN', "IW=2_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False",
                          "IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False")
s = subset(plantimedata, agent_type==levels(plantimedata$agent_type)[4]) ## ordered by IW1
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$game_name
p = ggplot()+
  geom_bar(data=subset(plantimedata, agent_type%in%main_plot_agent_types & agent_type!='DDQN'),#(log(human_normed_composite_ratio)>-3)),
           aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=subset(plantimedata, agent_type%in%main_plot_agent_types  & !(log(human_normed_composite_ratio)>-3)),
             aes(x=game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("Human-normed performance")+xlab('Game name')+ylim(-10,10)
# tickmarks = c(10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                       breaks=c(levels(plantimedata$agent_type)[4], levels(plantimedata$agent_type)[3], "DDQN"),
                       labels=c("EMPA (IW1)", "EMPA (IW2)", "DDQN")) + scale_color_manual(values=colors,name="Model",
                                                                                         breaks=c(levels(plantimedata$agent_type)[4], levels(plantimedata$agent_type)[3], "DDQN"),
                                                                                         labels=c("EMPA (IW1)", "EMPA (IW2)", "DDQN"))
## 14x10

tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p = ggplot(subset(plantimedata, short_agent_type %in% c('DDQN', 'IW1')), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
 geom_histogram(stat='bin',bins=50, position='identity', alpha=.8) +scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_color_manual(values=colors)+scale_fill_manual(values=colors,name="Model",
                                                                                  breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                                                                                  labels=c("DDQN", 'EMPA')) +
  scale_color_manual(values=colors,name="Model",
                    breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                    labels=c("DDQN", 'EMPA'))+ xlab("Human-normed performance") + ylab("Number of games")+ geom_vline(xintercept=0,linetype='dashed',size=.4)
p ## 6x8 performance_distribution_histogram


## Plot distribution of exploration scores.
exploration_lesion_and_DQN_names = c("IW1","DDQN", "ε-greedy DS, 1k","ε-greedy DS, 2k", "ε-greedy, 1k", "ε-greedy, 2k")
colors = c('steelblue3',"grey50", 'slateblue1', 'slateblue2', 'slateblue3', 'slateblue4')
names(colors) = exploration_lesion_and_DQN_names
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p = ggplot(subset(plantimedata, short_agent_type %in% exploration_lesion_and_DQN_names), aes(x=log(human_normed_composite_ratio), fill=short_agent_type, color=short_agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarklabels)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.4)
p # 6x9


## Plot a bit of each type of lesion (exploration and planning)
# plan_and_exploration_lesion_names = c("IW1","DDQN", "ε-greedy DS, 1k", "ε-greedy, 1k", "No subgoals + no gradient" , "No IW", "No subgoals + no gradient + no IW")
# colors = c('steelblue3',"grey50", 'slateblue1', 'slateblue3', 'goldenrod1','darkslategray2', 'darkolivegreen3')
plan_and_exploration_lesion_names = c("IW1","DDQN", "No subgoals + no gradient" , "No IW", "No subgoals + no gradient + no IW")
colors = c('steelblue3',"grey50", 'goldenrod1','darkslategray2', 'darkolivegreen3')
names(colors) = plan_and_exploration_lesion_names
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p = ggplot(subset(plantimedata, short_agent_type %in% plan_and_exploration_lesion_names), aes(x=log(human_normed_composite_ratio), fill=short_agent_type, color=short_agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarklabels)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.4)
p # 6x9


#### use this to generate the legend, then cut/paste it in illustrator.
main_plot_agent_types = c('DDQN', "IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False")
s = subset(plantimedata, agent_type==levels(plantimedata$agent_type)[4]) ## should be IW1
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$game_name
p = ggplot()+
  geom_bar(data=subset(plantimedata, (agent_type%in%main_plot_agent_types)),
           aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=subset(plantimedata, agent_type%in%main_plot_agent_types  & !(log(human_normed_composite_ratio)>-3)),
             aes(x=game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("Human-normed performance")+xlab('Game name')+ylim(-10,10)
tickmarks = c(10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c(levels(plantimedata$agent_type)[4], "DDQN"),
                      labels=c("EMPA (IW1)","DDQN")) +
  scale_color_manual(values=colors,name="Model",
                     breaks=c(levels(plantimedata$agent_type)[4],"DDQN"),
                     labels=c("EMPA (IW1)","DDQN"))


#### Plot IW1 alone
##

main_plot_agent_types = c('DDQN', "IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False")
s = subset(plantimedata, agent_type==levels(plantimedata$agent_type)[4]) ## should be IW1
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$game_name
p = ggplot()+
  geom_bar(data=subset(plantimedata, (agent_type%in%main_plot_agent_types & agent_type!='DDQN')),
           aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=subset(plantimedata, agent_type%in%main_plot_agent_types  & !(log(human_normed_composite_ratio)>-3)),
             aes(x=game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("Human-normed performance")+xlab('Game name')+ylim(-10,10)
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
tickmarklabels = c("<10e8",10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarklabels)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                      labels=c("DDQN", "EMPA (IW1)")) +
                      scale_color_manual(values=colors,name="Model",
                                         breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                                        labels=c("DDQN", "EMPA (IW1)"))


#### mess with this to get error bars in main figure.

p = ggplot()+
  geom_bar(data=subset(plantimesummary, (agent_type%in%main_plot_agent_types & agent_type!='DDQN')),
           aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge', fun.y='mean') #+
  # p = ggplot(s, aes(x=short_agent_type, y=normed_plan_nodes_per_step, fill=short_agent_type)) +
  # geom_bar(position='dodge', stat='summary', fun.y='mean')+
  geom_linerange(aes(ymin=log(human_normed_composite_ratio-log(ci), ymax=human(human_normed_composite_ratio)+log(ci))))+

# geom_point(data=subset(plantimedata, agent_type%in%main_plot_agent_types  & !(log(human_normed_composite_ratio)>-3)),
           # aes(x=game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  # scale_x_discrete(limits=ordered_names)+

  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("Human-normed performance")+xlab('Game name')+ylim(-10,10)
tickmarks = c(10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                      labels=c("DDQN", "EMPA (IW1)")) +
  scale_color_manual(values=colors,name="Model",
                     breaks=c("DDQN", levels(plantimedata$agent_type)[4]),
                     labels=c("DDQN", "EMPA (IW1)"))


#### Plot IW2 alone

main_plot_agent_types = c('DDQN', "IW=2_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False")

s = subset(plantimedata, agent_type==levels(plantimedata$agent_type)[3]) ## should be IW2
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$game_name
p = ggplot()+
  geom_bar(data=subset(plantimedata, (agent_type%in%main_plot_agent_types & agent_type!='DDQN')), #& (log(human_normed_composite_ratio)>-3)),
           aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=subset(plantimedata, agent_type%in%main_plot_agent_types  & !(log(human_normed_composite_ratio)>-3)),
             aes(x=game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("Human-normed performance")+xlab('Game name')+ylim(-10,10)
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
tickmarklabels = c("<10e-8",10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)

logtickmarks=(log(tickmarks))
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarklabels)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c(levels(plantimedata$agent_type)[3], "DDQN"),
                      labels=c("EMPA (IW2)","DDQN")) + scale_color_manual(values=colors,name="Model",
                                                                                         breaks=c(levels(plantimedata$agent_type)[3],"DDQN"),
                                                                                         labels=c("EMPA (IW2)", "DDQN"))

## 14x10

## change -Inf to something readable so that plots come out.

## Make short names for agent_types
plantimedata$short_agent_type = NA
for (i in 1:length(plantimedata$agent_type)){
  agent = plantimedata$agent_type[i]
  if(agent=='human'){
    short_type = 'human'
  }
  if(agent=='DDQN'){
    short_type = 'DDQN'
  }
  if(agent=="IW=2_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False"){
    short_type = 'IW2'
  }
  if(agent=="IW=1_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False"){
    short_type = 'IW1'
  }
  if(agent=="IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'IW1'
  }
  if(agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'No subgoals'
  }
  if(agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'No goal gradient'
  }
  if(agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'No subgoals + no gradient'
  }
  if(agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'No IW'
  }
  if(agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW-AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR"){
    short_type = 'No subgoals + no gradient + no IW'
  }
  if (agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=1000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR"){
    short_type = 'ε-greedy DS, 1k'
  }
  if (agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=2000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR"){
    short_type = 'ε-greedy DS, 2k'
  }
  if (agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR"){
    short_type = 'ε-greedy, 1k'
  }
  if (agent=="IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR"){
    short_type = 'ε-greedy, 2k'
  }
  plantimedata$short_agent_type[i] = short_type
}
plantimedata$short_agent_type = as.factor(plantimedata$short_agent_type)
##plot exploration lesions


for (i in 1:length(plantimedata$human_normed_composite_ratio)){
  if (plantimedata$human_normed_composite_ratio[i]==0){
    plantimedata$human_normed_composite_ratio[i]=10e-8
  }
}
plantimedata$log_human_normed_composite_ratio = log(plantimedata$human_normed_composite_ratio)



exploration_lesion_names = c("IW1", "ε-greedy DS, 1k","ε-greedy DS, 2k", "ε-greedy, 1k", "ε-greedy, 2k")
colors = c('steelblue3','slateblue1', 'slateblue2', 'slateblue3', 'slateblue4')
names(colors) = exploration_lesion_names
lesions = exploration_lesion_names
planner_lesion_names = c('IW1', 'No subgoals', 'No goal gradient', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW')
colors = c('steelblue3','goldenrod1', 'goldenrod1', 'goldenrod1', 'darkslategray2', 'darkolivegreen3')
names(colors) = planner_lesion_names
lesions = planner_lesion_names
s = subset(plantimedata, short_agent_type=='IW1')
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$game_name
plots = list()
for (i in 1:length(lesions)){
  types_to_plot = c(lesions[i])#c('IW1')#, lesions[i])
  # names(colors)=types_to_plot
  colorScale = scale_color_manual(name="short_agent_type", values=colors)
  p = ggplot()+
    geom_bar(data=subset(plantimedata, short_agent_type %in% types_to_plot),
             aes(x=game_name, y=log(human_normed_composite_ratio), fill=as.factor(short_agent_type)), stat='identity',position='dodge')+
    scale_x_discrete(limits=ordered_names)+
    theme(legend.position="none")+
    colorScale+
  ylab("")+xlab("")+geom_hline(yintercept=0,size=.4)
      # ylab("Human-normed performance")+xlab('Game name')+ylim(-10,5)

        # theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  # tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
  tickmarks = c(10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2)
  logtickmarks=(log(tickmarks))
  p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(log(10e-4), log(100)))
  p=p+theme(axis.line.y=element_blank(),axis.text.y=element_blank(), axis.ticks.y=element_blank())
  
  # p+scale_fill_manual(values=colors)
  
  p = p+ scale_fill_manual(values=colors,name="Model",
                           breaks=c(types_to_plot[1]),
                           labels=c(types_to_plot[1]))
  p  
  # scale_fill_manual(values=colors,name="Model",
                        # breaks=c(types_to_plot[1], types_to_plot[2]),
                        # labels=c("EMPA (IW1)", types_to_plot[2]))
  
  plots[[i]] = p
  
  }

layout = matrix(c(1:length(plots)), ncol=length(plots), byrow=TRUE)
m = multiplot(plotlist = plots, layout=layout)
##24x10



##### planner lesion performance summary
models_to_plot = planner_lesion_names
s = summarySE(subset(plantimedata, short_agent_type%in%models_to_plot), 
              measurevar="log_human_normed_composite_ratio", groupvars=c("short_agent_type"), na.rm=TRUE)

tickmarks = c(10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2)
logtickmarks = log(tickmarks)
p = ggplot(s, aes(x=short_agent_type, y=log_human_normed_composite_ratio, fill=short_agent_type)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean')+geom_linerange(aes(ymin=log_human_normed_composite_ratio-ci, ymax=log_human_normed_composite_ratio+ci))
p=p+colorScale+scale_fill_manual(values=colors, name="Lesion",
                                 breaks=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'),
                                 labels=c('EMPA', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW')) #+
  # scale_x_discrete(limits=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'),
                   # labels=c('EMPA', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW')) + xlab('Lesion') + ylab('Human-normed performance')
p=p+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p ## 10x24



###Exploration lesions -- barplot for all 90 games
models_to_plot = exploration_lesion_and_DQN_names
s = summarySE(subset(plantimedata, short_agent_type%in%models_to_plot), 
              measurevar="log_human_normed_composite_ratio", groupvars=c("short_agent_type"), na.rm=TRUE)

tickmarks = c(10e-7, 10e-6, 10e-5, 10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2)
logtickmarks = log(tickmarks)
xbreaks = c('DDQN','IW1', 'ε-greedy DS, 1k', 'ε-greedy DS, 2k', 'ε-greedy, 1k', 'ε-greedy, 2k')
xlabels = c('DDQN','EMPA', 'ε-greedy DS, 1k', 'ε-greedy DS, 2k', 'ε-greedy, 1k', 'ε-greedy, 2k')
p = ggplot(s, aes(x=short_agent_type, y=log_human_normed_composite_ratio, fill=short_agent_type)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean')+geom_linerange(aes(ymin=log_human_normed_composite_ratio-ci, ymax=log_human_normed_composite_ratio+ci))

p=p+colorScale+scale_fill_manual(values=colors, name="Lesion",
                                 breaks=xbreaks,
                                 labels=xlabels)+
 xlab('Lesion') + ylab('Human-normed performance')
p=p+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)+scale_x_discrete(breaks=xbreaks, labels=xlabels)
p ## 10x24



## exploration lesions -- barplot only for games the models solved
models_to_plot = exploration_lesion_and_DQN_names
plantimedata_models = subset(plantimedata, short_agent_type%in%models_to_plot)
nonzero_dataframe = c()
for (game in unique(plantimedata_models$game_name)){
  s = subset(plantimedata_models, game_name==game)
  if (min(s$level_percentage)>0){
    nonzero_dataframe = rbind(nonzero_dataframe, s)
  }
}
##num_games that all models solved: length(unique(nonzero_dataframe)$game_name) (31)
s = summarySE(nonzero_dataframe, 
              measurevar="log_human_normed_composite_ratio", groupvars=c("short_agent_type"), na.rm=TRUE)

tickmarks = c(10e-7, 10e-6, 10e-5, 10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2)
logtickmarks = log(tickmarks)
xbreaks = c('DDQN','IW1', 'ε-greedy DS, 1k', 'ε-greedy DS, 2k', 'ε-greedy, 1k', 'ε-greedy, 2k')
xlabels = c('DDQN','EMPA', 'ε-greedy DS, 1k', 'ε-greedy DS, 2k', 'ε-greedy, 1k', 'ε-greedy, 2k')
p = ggplot(s, aes(x=short_agent_type, y=log_human_normed_composite_ratio, fill=short_agent_type)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean')+geom_linerange(aes(ymin=log_human_normed_composite_ratio-ci, ymax=log_human_normed_composite_ratio+ci))
p=p+colorScale+scale_fill_manual(values=colors, name="Lesion",
                                 breaks=xbreaks,
                                 labels=xlabels)+
  xlab('Lesion') + ylab('Human-normed performance')
p=p+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p ## 10x24


df = data.frame(game_name=as.character(), agent_type=as.character(), short_agent_type=as.character(), max_steps=as.numeric(), planning_time=as.numeric(), min_planning_time=as.numeric())
IW2data = plantimedata[which(plantimedata$short_agent_type=='IW2'),]

savedplantimedata=plantimedata
plantimedata$normed_plan_nodes_per_step=NA
for (i in 1:length(unique(plantimedata$game_name))){
 game=unique(plantimedata$game_name)[i] 
 min_nodes_per_step = min(plantimedata[which( (plantimedata$short_agent_type %in% c('IW2', planner_lesion_names)) & (plantimedata$game_name==game)),]$plan_nodes_per_step)
 # MEP_nodes_per_step = plantimedata[which( (plantimedata$short_agent_type=='IW2')& (plantimedata$game_name==game)),]$plan_nodes_per_step
 for (model in c('IW2', planner_lesion_names)){
   row = plantimedata[which((plantimedata$short_agent_type==model)&(plantimedata$game_name==game)),]
   plantimedata[which((plantimedata$short_agent_type==model)&(plantimedata$game_name==game)),]$normed_plan_nodes_per_step = min_nodes_per_step/row$plan_nodes_per_step
   }
}

### Make plot of summarized planner efficiency
# models_to_plot = c('IW2', planner_lesion_names)
# colors = c('steelblue3','goldenrod1', 'goldenrod1', 'goldenrod1', 'indianred1')
# names(colors)=models_to_plot
# colorScale = scale_color_manual(name="short_agent_type", values=colors)
models_to_plot = planner_lesion_names
s = summarySE(subset(plantimedata, short_agent_type%in%models_to_plot), 
              measurevar="normed_plan_nodes_per_step", groupvars=c("short_agent_type"), na.rm=TRUE)
p = ggplot(s, aes(x=short_agent_type, y=normed_plan_nodes_per_step, fill=short_agent_type)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean')+geom_linerange(aes(ymin=normed_plan_nodes_per_step-ci, ymax=normed_plan_nodes_per_step+ci))
p=p+colorScale+scale_fill_manual(values=colors, name="Lesion",
                                 breaks=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'),
                                 labels=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'))+
  scale_x_discrete(limits=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'),
                   labels=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW')) + xlab('Lesion') + ylab('Planner efficiency')
p

models_to_plot
plots = list()
for (i in 1:length(models_to_plot)){
  model = rev(models_to_plot)[i]## reversing list here so we get the plot that works when we flip 90 degrees
  p = ggplot(subset(plantimedata, short_agent_type==model), 
             aes(x=game_name, y=normed_plan_nodes_per_step, fill=short_agent_type))+
    geom_bar(position='dodge',stat='identity')+ylim(0,1)+xlab("Game name") +ylab("Planner efficiency")+theme(axis.title.x=element_blank(),
                                                                axis.text.x=element_blank(),
                                                                axis.ticks.x=element_blank())+colorScale+theme(legend.position="none")+
    # colorScale+scale_fill_manual(values=colors, name="",
    #                              breaks=c('IW2', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW'),
    #                              labels=c('IW2', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW'))+
    colorScale+scale_fill_manual(values=colors, name="Lesion",
                                 breaks=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'),
                                 labels=c('IW1', 'No goal gradient', 'No subgoals', 'No subgoals + no gradient', 'No IW', 'No subgoals + no gradient + no IW'))+
        scale_x_discrete(limits=unique(plantimedata$game_name))#+scale_fill_manual(name="Game", breaks=unique(plantimedata$game_name))
  p
  # p=p+coord_flip()
  plots[[i]]=p
}
layout = matrix(c(1:length(models_to_plot)), ncol=1, byrow=TRUE)
m = multiplot(plotlist = plots, layout=layout)
## 10x24

summarise(subset(plantimedata, short_agent_type%in%c('IW2', lesions), comp_ratio_mean=mean(human_normed_composite_ratio), comp_ratio_sd=sd(human_normed_composite_ratio))

## Entropy-reduction plots
p = ggplot(data, aes(x=cumulative_steps,y=entropy,color=agent_type))
p=p+geom_point()+ theme(legend.position="none")+geom_smooth()
p
          


## same thing but not grouped by game. not easy to read.
# p = ggplot(plantimedata, aes(x=reorder(game_name,-level_percentage), y=level_percentage, fill=factor(agent_type))) +
#   geom_bar(position='dodge', stat='identity')+
#   theme(axis.text.x = element_text(angle = 90, hjust = 1))+scale_fill_manual(values=colors)
# p
## save as 6x72



# ## you're unable to get both models on this plot. why??
# s = subset(plantimedata, (agent_type%in%c('DDQN',levels(plantimedata$agent_type)[4])) & (!is.na(score_efficiency)|score_efficiency>0.005 ))
# colors = c('steelblue3', 'steelblue3', 'steelblue3', 'steelblue3',
#            'firebrick2', 'tomato2', 'salmon',
#            'purple2', 'mediumorchid2', 
#            'darkslategray3', 'mediumpurple2', 'aquamarine3', 'coral3')
# 
# names(colors)=levels(s$agent_type)
# colorScale = scale_color_manual(name="agent_type", values=colors)
# 
# p = ggplot(s, aes(x=reorder(game_name,score_efficiency), y=score_efficiency, fill=agent_type))+
#   geom_bar(stat='identity',position='dodge')+theme(legend.position="none")+
#   colorScale+
#   scale_fill_manual(values=colors) +
#   theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab("max_score / steps")+xlab('game name')
# p+coord_flip()


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
path = '~/Projects/atari/vgdl/humandata_ratings/ratings'
ratingpaths = list.files(path)
ratings = list()
for (rating in ratingpaths){
  ratingpath = paste(path, '/', rating, sep='')
  r=read.csv(ratingpath, header=TRUE, na.strings='NA')
  if (length(ratings)==0){
    ratings = r
  }
  else{
    ratings = rbind(ratings,r)
  }
}
substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}
find_source_game = function(name){
  if (substrRight(name,1)%in%c("1","2","3","4")){
    return(substr(name,0,nchar(name)-2))
  }
  else{
    return(name)}
}
find_variant_number = function(name){
  lastchar = substrRight(name,1)
  if (lastchar%in%c("1","2","3","4")){
    return(lastchar)
  }
  else{
    return('0')
  }
}
ratings$game_name = as.factor(ratings$gameName)
ratings$source_game_name = as.factor(as.character(lapply(as.vector(ratings$game_name), find_source_game)))
ratings$variant_number = as.factor(as.character(lapply(as.vector(ratings$game_name), find_variant_number)))
for (i in 1:length(ratings$difficulty)){
  if (!is.na(ratings$difficulty[i]) & ratings$difficulty[i]=="None"){
    ratings$difficulty[i]=NA
  }
  if (ratings$interestingness[i]=="None"){
    ratings$interestingness[i]=NA
  }
}
ratings$difficulty = as.numeric(ratings$difficulty)
ratings$interestingness = as.numeric(ratings$interestingness)
## you also have enjoyability

s = summarySE(ratings, measurevar="difficulty", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=difficulty)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=difficulty-ci, ymax=difficulty+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Difficulty')+scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
#+ theme(axis.title.x=element_blank(),axis.text.x=element_blank(),axis.ticks.x=element_blank())+theme(legend.position='bottom')
p  
##save 12x6

s = summarySE(ratings, measurevar="interestingness", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=interestingness)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=interestingness-ci, ymax=interestingness+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Interestingness') +scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
#+ theme(axis.title.x=element_blank(),axis.text.x=element_blank(),axis.ticks.x=element_blank())+theme(legend.position='bottom')
p  
##save 12x6


##for playing around with format
# p = ggplot(subset(s, source_game_name%in%c('push_boulders','relational')), aes(x=reorder(variant_number, as.numeric(variant_number)), y=difficulty))+
# geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=difficulty-ci, ymax=difficulty+ci))+
# facet_wrap(~source_game_name)
# p


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


# newdataframe = subset(data, game_name==levels(dataframe$game_name)[1])
# for (i in 2:length(levels(dataframe$game_name))){
#   name = levels(dataframe$game_name)[i]
#   s = subset(data, game_name==levels(dataframe$game_name)[i])
#   for (j in 1:length(strings_to_remove)){
#     string_to_remove = strings_to_remove[j]
#     if (grepl(string_to_remove, name)){
#       newname = substr(name, nchar(string_to_remove)+2, nchar(name))
#       s$game_name = as.factor(newname)
#     }
#     newdataframe = rbind(newdataframe, s)
#   }
# }

remove_string_from_name = function(name){
  strings_to_remove = c('gvgai_variant','expt_variant','variant_expt', 'variant','gvgai', 'expt')
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


## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  library(plyr)
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  # datac$measurevar = datac$mean
  colnames(datac)[colnames(datac)=="mean"] <- measurevar
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}
