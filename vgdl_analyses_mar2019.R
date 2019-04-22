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

## everything starting mar23 has no 15-loss cutoff.
## mar28: 10 runs of EMPA with no limit on losses.
## mar30: unclear
## apr4: e-greedy and random policy, both 10x. Random policy incomplete (got kicked off om2)
EMPA_dates = list('mar28', 'apr4')
dqn_path = '~/Projects/atari/vgdl/dqn_data/'
humandatapaths = list.files("~/Projects/atari/vgdl/humandata")

### Toggle the below line to alter what you're reading in
data_to_load = 'EMPA'
data_to_load = 'human'
data_to_load = 'DDQN'

if (data_to_load == 'EMPA'){
  dates_or_groups = EMPA_dates
}else if (data_to_load == 'human'){
  dates_or_groups = groups
}else if (data_to_load == 'DDQN'){
  dates_or_groups = NA #doesn't matter
}

EMPAdata = load_reward_data('EMPA', dates_or_groups)
EMPA_variants = filter(EMPAdata, agent_type!='EMPA')
humandata = load_reward_data('human', dates_or_groups)
dqndata = load_reward_data('DDQN', dates_or_groups)

alldata = rbind(EMPAdata, humandata, dqndata)
human_normed_data = make_human_normed_data(alldata)

colors = c('steelblue1',
           'purple2', #'mediumorchid2',
           'firebrick2',# 'seagreen3','darkolivegreen1',
           'palegreen3',# 'tomato2', 'salmon', 
           'gray50', 'gray52', 'gray54')
           # 'darkslategray3', 'darkslategray2', 'darkslategray1')#, 'mediumpurple2', 'aquamarine3', 'coral3')
names(colors)=unique(alldata$agent_type)


## density plot summary plot of overall results -- easy to look at.
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
p = ggplot(filter(human_normed_data, agent_type!='human'), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.4)
p # 6x9


## one plot per game summary plot of overall results -- easy to look at.
p = ggplot(subset(human_normed_data), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+scale_fill_manual(values=colors)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')
p
## save as 10x16


# complete_games = c()
# overcomplete_games = c()
# for (game in unique(EMPA_data$game_name)){
#   l = length(unique(filter(EMPA_data, game_name==game)$subject_ID))
#   if (l!=10){
#     overcomplete_games = c(overcomplete_games, game)
#   }else{
#     complete_games = c(complete_games, game)
#   }
# }

# for (game in complete_games){
#   p = ggplot(filter(EMPA_data, game_name==game), aes(x=cumulative_timestep, y=cumulative_wins, color=subject_ID))
#   p = p+geom_point()+geom_smooth()
#   # p
#   newdir='~/Projects/atari/vgdl/empa_plots/by_subject/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=5) 
# }


make_human_normed_data = function(dataframe){
  ## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
  plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                            max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                            level_num=as.numeric(), level_efficiency=as.numeric())
  
  for (j in 1:length(unique(dataframe$agent_type))){
    agent = unique(dataframe$agent_type)[j]
    print(agent)
    for (i in 1:length(unique(dataframe$game_name))){
      g = subset(dataframe, game_name==unique(dataframe$game_name)[i])
      print(unique(dataframe$game_name)[i])
      s = subset(g, agent_type==agent)
      if (length(s$cumulative_steps)>0){
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
        
        ## mean vector of win numbers
        mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
        ##mean of vector steps-to-win ratios
        l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
        
        ## the row we want
        r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
        ## take only the relevant columns and put them in the new data frame
        new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                         max_steps=r$cumulative_steps, mean_levels_won=mean_wins,
                         level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                         level_efficiency=l_e)
        plantimedata = rbind(plantimedata, new)
      }
    }
  }
  
  
  plantimedata = mutate(plantimedata, level_percentage=mean_levels_won/level_num)
  plantimedata = mutate(plantimedata, composite_ratio = level_percentage*level_efficiency)
  
  plantimedata$human_normed_composite_ratio=NA
  ##norm by human level_efficiency
  for (i in 1:length(unique(plantimedata$game_name))){
    game = unique(plantimedata$game_name)[i]
    human_composite_ratio = subset(plantimedata, agent_type=='human' & game_name==game)$composite_ratio
    for (agent in unique(plantimedata$agent_type)){
      row = plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]
      plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    }
  }
  
  for (i in 1:length(plantimedata$human_normed_composite_ratio)){
    if (plantimedata$human_normed_composite_ratio[i]==0){
      plantimedata$human_normed_composite_ratio[i]=10e-8
    }
  }
  return(plantimedata)
  }

load_reward_data = function(data_to_load, dates_or_groups){
    if (data_to_load=='EMPA'){
      data = c()
      for (date in dates_or_groups){
      path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      
      # if ('exploration_burn_ins' %in% names(d)){
      #   d$exploration_burn_ins = as.numeric(d$exploration_burn_ins) ## you might want to make this as.numeric()
      # }else{
      #   d$exploration_burn_ins = NA
      # }
      
      if(length(data)==0){
        data = d
      }
      else{
        for(colname in names(d)){
          if (!(colname %in% names(data))){
            data[,colname] = NA
          }
        }
        for(colname in names(data)){
          if(!(colname %in% names(d))){
            d[,colname]=NA
          }
        }
        data = rbind(data,d)
      }
      }
      data$modelrun_ID = as.factor(data$modelrun_ID)
      data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
      data$long_agent_type = as.factor(data$agent_type)
      e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      data$agent_type = NA
      if (e_greedy_1a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1a,]$agent_type = 'e-greedy .1'
      }
      if (e_greedy_1b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1b,]$agent_type = 'e-greedy .1'
        
      }
      if (e_greedy_05 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_05,]$agent_type = 'e-greedy .05'
      }
      for (agent in unique(data$long_agent_type)){
        if (grepl('rand=True', agent)){
          data[grepl('rand=True', data$long_agent_type),]$agent_type = 'random policy'
        }
      }
      if (NA %in% unique(data$agent_type)){
        data[is.na(data$agent_type),]$agent_type = 'EMPA'
      }
      
      data$score = as.numeric(as.character(data$sparse_score))
      data = select(data, -timestep, -level_max_score, -cumulative_max_score, -sparse_score, -level_accumulated_score, 
                    -episode_end, -win, -planner_nodes, -planner_settings, -cumulative_planner_nodes, 
                    -cumulative_timestep, -entropy, -condition, -exploration_burn_ins)
      if ('time_elapsed'%in%names(data)){
        data = select(data, -time_elapsed)
      }
      if ('sparse_levels_won'%in%names(data)){
        data = select(data, -sparse_levels_won)
      }
      data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }else if (data_to_load == 'DDQN'){
    dqndata = list()
    for (gamefile in list.files(dqn_path)){
      filename = paste(dqn_path,gamefile,sep='')
      if(grepl('dqn/', filename)){
        gamenamestart = unlist(gregexpr('dqn/',filename))+nchar('dqn/')
        gamenameend = unlist(gregexpr('_reward', filename))-1        
      }else if (grepl('dqn_data/', filename)){
        gamenamestart = unlist(gregexpr('dqn_data/',filename))+nchar('dqn_data/')
        gamenameend = unlist(gregexpr('_DDQN_reward', filename))-1  
      }

      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))-1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      if ((grepl('101', filename) || grepl('trial1', filename) || grepl('decay1k', filename))){
        d$agent_type = as.factor("DDQN 1k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation. 
      }else if ((grepl('102', filename)|| grepl('trial2', filename) || grepl('decay10k', filename))){
        d$agent_type = as.factor("DDQN 10k")
      }else if ((grepl('103', filename)||grepl('trial3', filename) || grepl('decay100k', filename))){
        d$agent_type = as.factor("DDQN 100k")
      }else{
        d$agent_type = as.factor("DDQN")
      }
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      for (i in 2:length(d$level)){
        if (d$level[i]>d$level[i-1]){
          d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
          # d$sparse_levels_won[i] = d$cumulative_wins[i]
        }
        else{
          d$cumulative_wins[i] = d$cumulative_wins[i-1]
        }
      }
      d$level_number = d$level
      
      dqndata = rbind(dqndata,d)
    }
    data = dqndata
    data$modelrun_ID = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
    
  }else if (data_to_load == 'human'){
    humandata = list()
    for (humandatapath in humandatapaths){
      path = paste('~/Projects/atari/vgdl/humandata/',humandatapath, sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      if (length(humandata)==0){
        humandata = d
      }
      else{
        humandata = rbind(humandata,d)
      }
    }
    humandata$long_agent_type=as.factor('human')
    humandata$agent_type=as.factor('human')
    humandata$modelrun_ID = as.factor('oct29')
    humandata$condition = as.factor('full')
    
    humandata$game_name = as.factor(humandata$game_name)
    humandata = select(humandata, -levels_lost, -group, -gameNumber, -gameRound)
    data = humandata
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }
  
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  return (data)
}

create_rand_string <- function() {
  a <- do.call(paste0, replicate(1, sample(LETTERS, 1, TRUE), FALSE))
  paste0(a, sprintf("%04d", sample(9999, 1, TRUE)), sample(LETTERS, 1, TRUE))
}



game_names = c(levels(data$game_name))
