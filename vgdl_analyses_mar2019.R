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


EMPA_dates = list('mar28')
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

EMPAdata = load_reward_data('EMPA')
humandata = load_reward_data('human')
dqndata = load_reward_data('DDQN')

alldata = rbind(EMPAdata, humandata, dqndata)
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

## now streamline naming. first between dqn data and EMPA_data and then with human_data.

load_reward_data = function(data_to_load){
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
      e_greedy_1='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      data$agent_type = NA
      if (e_greedy_1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1,]$agent_type = 'e-greedy .1'
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
                    -episode_end, -win, -sparse_levels_won, -planner_nodes, -planner_settings, -cumulative_planner_nodes, 
                    -cumulative_timestep, -time_elapsed, -entropy, -condition, -exploration_burn_ins)
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
